import pandas as pd

from src.cleaning import clean_products, clean_reviews, parse_sales_lower_bound
from src.config import load_config


def test_parse_sales_lower_bound_handles_censoring() -> None:
    assert parse_sales_lower_bound("1,000+") == (1000.0, True)
    assert parse_sales_lower_bound(31) == (31.0, False)


def test_product_cleaning_removes_only_exact_duplicates() -> None:
    raw = pd.DataFrame(
        {
            "商品名称": ["A 考古盲盒", "A 考古盲盒", "A 考古盲盒"],
            "价格": [50, 50, 60],
            "Unnamed: 2": [None, None, None],
            "商家": ["测试旗舰店", "测试旗舰店", "其他店"],
            "销售量": ["100+", "100+", 5],
        }
    )
    cleaned, report = clean_products(raw, load_config())
    assert len(cleaned) == 2
    assert report["exact_duplicates_removed"] == 1
    assert cleaned["product_id"].is_unique


def test_review_cleaning_deduplicates_and_keeps_chinese_text() -> None:
    raw = pd.DataFrame({"comment": ["包装很好", "包装很好", "价格有点贵"]})
    cleaned, report = clean_reviews(raw)
    assert len(cleaned) == 2
    assert report["exact_duplicates_removed"] == 1
    assert "Packaging" in cleaned.loc[cleaned["review_text_zh"] == "包装很好", "aspects"].iloc[0]

