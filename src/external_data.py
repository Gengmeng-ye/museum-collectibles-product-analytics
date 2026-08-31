import hashlib
import re
from html import unescape
from pathlib import Path

import pandas as pd

from src.cleaning import _stable_id
from src.rules import normalize_text


def _text(fragment: str) -> str:
    return normalize_text(unescape(re.sub(r"<[^>]+>", " ", fragment)))


def read_hooos_product_snapshots(directory: Path) -> pd.DataFrame:
    """Parse saved public listing snapshots without making a network request."""
    rows: list[dict] = []
    for page_path in sorted(directory.glob("page_*.html")):
        html = page_path.read_text(encoding="utf-8")
        list_match = re.search(r"<main>.*?<ul>(.*?)</ul>", html, flags=re.DOTALL)
        if not list_match:
            raise ValueError(f"No product list found in {page_path}")
        for position, item in enumerate(re.findall(r"<li>(.*?)</li>", list_match.group(1), re.DOTALL), 1):
            link = re.search(r'<a href="([^"]*goods_[^"]+)">', item)
            title = re.search(r"<h4>(.*?)</h4>", item, re.DOTALL)
            price = re.search(r"<em><b>([0-9.]+)</b>", item)
            category = re.search(r"<u>(.*?)</u>", item, re.DOTALL)
            seller_block = re.search(r"<p[^>]*>(.*?)</p>", item, re.DOTALL)
            if not (link and title and price and seller_block):
                continue
            seller_parts = [_text(value) for value in re.findall(r"<i>(.*?)</i>", seller_block.group(1), re.DOTALL)]
            sales_text = next((value for value in seller_parts if value.startswith("销量")), "")
            seller = next(
                (value for value in reversed(seller_parts) if not value.startswith("销量") and value not in {"淘宝好物", "天猫好物"}),
                "",
            )
            source_url = "https://tao.hooos.com" + link.group(1)
            rows.append(
                {
                    "source_page": int(re.search(r"(\d+)", page_path.stem).group(1)),
                    "source_position": position,
                    "product_name_zh": _text(title.group(1)),
                    "seller_name_zh": seller,
                    "price_cny": float(price.group(1)),
                    "sales_display": sales_text.removeprefix("销量") or pd.NA,
                    "source_category_zh": _text(category.group(1)) if category else pd.NA,
                    "source_url": source_url,
                    "source_snapshot": page_path.name,
                }
            )
    data = pd.DataFrame(rows)
    data["product_id"] = data["source_url"].map(lambda value: _stable_id("product", value))
    data["source_platform"] = "Hooos public Taobao/Tmall listing index"
    data["source_scope"] = "Museum cultural-creative blind-box tag, pages 1-5"
    data["collection_date"] = "2026-08-29"
    return data.drop_duplicates("product_id").reset_index(drop=True)


def read_figshare_reviews(path: Path) -> pd.DataFrame:
    data = pd.read_excel(path, usecols=["page", "userNick", "comment"])
    data = data.rename(columns={"comment": "review_text_zh", "userNick": "masked_user_name"})
    data["review_text_zh"] = data["review_text_zh"].map(normalize_text)
    data = data.loc[data["review_text_zh"].ne("")].drop_duplicates("review_text_zh").copy()
    data["review_id"] = data["review_text_zh"].map(lambda value: _stable_id("review", value))
    data["source_platform"] = "Taobao, redistributed via Figshare"
    data["source_dataset_doi"] = "10.6084/m9.figshare.30671120.v1"
    data["product_link_available"] = False
    return data.reset_index(drop=True)


def fixed_review_sample(reviews: pd.DataFrame, size: int, seed: int) -> pd.DataFrame:
    """Select a reproducible length-stratified sample to avoid only short generic reviews."""
    data = reviews.copy()
    data["review_length_chars"] = data["review_text_zh"].str.len()
    data["length_stratum"] = pd.qcut(data["review_length_chars"], q=5, duplicates="drop")
    sampled = (
        data.groupby("length_stratum", observed=True, group_keys=False)
        .sample(n=max(1, size // data["length_stratum"].nunique()), random_state=seed)
    )
    if len(sampled) < size:
        remaining = data.loc[~data.index.isin(sampled.index)]
        sampled = pd.concat([sampled, remaining.sample(size - len(sampled), random_state=seed)])
    return sampled.sample(frac=1, random_state=seed).head(size).drop(columns="length_stratum").reset_index(drop=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
