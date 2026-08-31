import hashlib
import re

import numpy as np
import pandas as pd

from src.config import AnalysisConfig
from src.rules import (
    CATEGORY_RULES,
    FORMAT_RULES,
    MUSEUM_RULES,
    detect_aspects,
    first_rule_match,
    normalize_text,
)


def _stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def parse_sales_lower_bound(value: object) -> tuple[float, bool]:
    if pd.isna(value):
        return np.nan, False
    text = normalize_text(value).replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return np.nan, False
    return float(match.group()), "+" in text


def assign_price_tier(price: float, config: AnalysisConfig) -> str:
    tiers = config.price_tiers
    if price <= tiers["budget_max"]:
        return "Budget (<=50 CNY)"
    if price <= tiers["mass_market_max"]:
        return "Mass Market (51-100 CNY)"
    if price <= tiers["premium_max"]:
        return "Premium (101-200 CNY)"
    return "High-end (>200 CNY)"


def clean_products(raw: pd.DataFrame, config: AnalysisConfig) -> tuple[pd.DataFrame, dict]:
    source_rows = len(raw)
    data = raw.dropna(axis=1, how="all").copy()
    expected = ["商品名称", "价格", "商家", "销售量"]
    missing = sorted(set(expected) - set(data.columns))
    if missing:
        raise ValueError(f"Missing product columns: {missing}")

    data = data.rename(
        columns={"商品名称": "product_name_zh", "价格": "price_cny", "商家": "seller_name_zh", "销售量": "sales_display"}
    )
    for column in ("product_name_zh", "seller_name_zh", "sales_display"):
        data[column] = data[column].map(normalize_text)
    data["price_cny"] = pd.to_numeric(data["price_cny"], errors="coerce")
    data["source_row_number"] = np.arange(2, len(data) + 2)
    data["is_exact_duplicate"] = data.duplicated(
        subset=["product_name_zh", "price_cny", "seller_name_zh", "sales_display"], keep="first"
    )
    duplicate_count = int(data["is_exact_duplicate"].sum())
    data = data.loc[~data["is_exact_duplicate"]].copy()

    parsed = data["sales_display"].map(parse_sales_lower_bound)
    data["sales_lower_bound"] = parsed.map(lambda x: x[0])
    data["sales_is_censored"] = parsed.map(lambda x: x[1])
    data["official_store_claimed"] = data["seller_name_zh"].str.contains(
        "旗舰店|博物院店铺", regex=True
    )
    combined_text = data["product_name_zh"] + " " + data["seller_name_zh"]
    data["museum_name"] = combined_text.map(
        lambda text: first_rule_match(text, MUSEUM_RULES, "Other / Unclear")
    )
    data["product_category"] = data["product_name_zh"].map(
        lambda text: first_rule_match(text, CATEGORY_RULES, "Other Cultural Product")
    )
    data["price_tier"] = data["price_cny"].map(lambda value: assign_price_tier(value, config))
    data["title_length_chars"] = data["product_name_zh"].str.len()
    data["product_id"] = data.apply(
        lambda row: _stable_id(
            "product",
            "|".join(
                [row["product_name_zh"], row["seller_name_zh"], str(row["price_cny"]), row["sales_display"]]
            ),
        ),
        axis=1,
    )
    data["source_platform"] = "Taobao (reported by legacy project)"
    data["source_scope"] = "First two search-result pages; collection date not retained"

    ordered = [
        "product_id", "source_row_number", "product_name_zh", "seller_name_zh", "price_cny",
        "sales_display", "sales_lower_bound", "sales_is_censored", "official_store_claimed",
        "museum_name", "product_category", "price_tier", "title_length_chars",
        "source_platform", "source_scope",
    ]
    report = {
        "source_rows": source_rows,
        "empty_columns_removed": int(raw.shape[1] - len(expected)),
        "exact_duplicates_removed": duplicate_count,
        "clean_rows": len(data),
        "missing_price": int(data["price_cny"].isna().sum()),
        "missing_sales": int(data["sales_lower_bound"].isna().sum()),
        "censored_sales_rows": int(data["sales_is_censored"].sum()),
        "duplicate_product_names_retained": int(data["product_name_zh"].duplicated().sum()),
    }
    return data[ordered].reset_index(drop=True), report


def clean_reviews(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    if "comment" not in raw.columns:
        raise ValueError("Missing review column: comment")
    data = raw[["comment"]].rename(columns={"comment": "review_text_zh"}).copy()
    data["review_text_zh"] = data["review_text_zh"].map(normalize_text)
    data = data.loc[data["review_text_zh"].ne("")].copy()
    data["is_exact_duplicate"] = data["review_text_zh"].duplicated(keep="first")
    duplicate_count = int(data["is_exact_duplicate"].sum())
    data = data.loc[~data["is_exact_duplicate"]].copy()
    data["review_id"] = data["review_text_zh"].map(lambda text: _stable_id("review", text))
    data["review_length_chars"] = data["review_text_zh"].str.len()
    data["aspects"] = data["review_text_zh"].map(detect_aspects).map(lambda x: "|".join(x))
    data["aspect_count"] = data["aspects"].map(lambda x: 0 if not x else len(x.split("|")))
    data["source_platform"] = "Taobao (reported by legacy project)"
    data["product_link_available"] = False
    report = {
        "source_rows": len(raw),
        "blank_rows_removed": int(len(raw) - len(raw.dropna(subset=["comment"]))),
        "exact_duplicates_removed": duplicate_count,
        "clean_rows": len(data),
        "reviews_with_no_detected_aspect": int(data["aspect_count"].eq(0).sum()),
    }
    ordered = [
        "review_id", "review_text_zh", "review_length_chars", "aspects", "aspect_count",
        "source_platform", "product_link_available",
    ]
    return data[ordered].reset_index(drop=True), report


def clean_external_products(raw: pd.DataFrame, config: AnalysisConfig) -> tuple[pd.DataFrame, dict]:
    data = raw.copy()
    source_rows = len(data)
    data["sales_display"] = data["sales_display"].astype("string")
    parsed = data["sales_display"].map(parse_sales_lower_bound)
    data["sales_lower_bound"] = parsed.map(lambda item: item[0])
    data["sales_is_censored"] = False
    data["sales_observed"] = data["sales_lower_bound"].notna()
    data["official_store_claimed"] = data["seller_name_zh"].str.contains(
        "旗舰店|博物馆文创|故宫淘宝", regex=True, na=False
    )
    combined = data["product_name_zh"] + " " + data["seller_name_zh"]
    data["museum_name"] = combined.map(
        lambda text: first_rule_match(text, MUSEUM_RULES, "Other / Unclear")
    )
    data["museum_ip_flag"] = data["museum_name"].ne("Other / Unclear")
    data["product_category"] = data["product_name_zh"].map(
        lambda text: first_rule_match(text, CATEGORY_RULES, "Other Cultural Product")
    )
    data["product_format"] = data["product_name_zh"].map(
        lambda text: first_rule_match(text, FORMAT_RULES, "Other Blind-box Format")
    )
    data["price_tier"] = data["price_cny"].map(lambda value: assign_price_tier(value, config))
    data["title_length_chars"] = data["product_name_zh"].str.len()
    data["keyword_excavation"] = data["product_name_zh"].str.contains("考古|挖掘|挖宝|寻宝")
    data["keyword_gift"] = data["product_name_zh"].str.contains("礼物|礼品|伴手礼|送朋友|生日")
    data["keyword_collectible"] = data["product_name_zh"].str.contains("收藏|手办|摆件|公仔")
    report = {
        "source_rows": source_rows,
        "clean_rows": len(data),
        "exact_duplicates_removed": source_rows - len(data),
        "missing_price": int(data["price_cny"].isna().sum()),
        "missing_sales": int(data["sales_lower_bound"].isna().sum()),
        "sales_coverage": float(data["sales_observed"].mean()),
    }
    return data.reset_index(drop=True), report


def clean_external_reviews(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    data = raw.copy()
    source_rows = len(data)
    data["review_text_zh"] = data["review_text_zh"].map(normalize_text)
    data = data.loc[data["review_text_zh"].ne("")].drop_duplicates("review_text_zh").copy()
    data["review_length_chars"] = data["review_text_zh"].str.len()
    data["aspects"] = data["review_text_zh"].map(detect_aspects).map("|".join)
    data["aspect_count"] = data["aspects"].map(lambda value: 0 if not value else len(value.split("|")))
    report = {
        "source_rows": source_rows,
        "clean_rows": len(data),
        "exact_duplicates_removed": source_rows - len(data),
        "reviews_with_no_detected_aspect": int(data["aspect_count"].eq(0).sum()),
    }
    ordered = [
        "review_id",
        "review_text_zh",
        "review_length_chars",
        "aspects",
        "aspect_count",
        "source_platform",
        "source_dataset_doi",
        "product_link_available",
    ]
    return data[ordered].reset_index(drop=True), report
