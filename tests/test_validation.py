import pandas as pd

from src.validation import validate_products, validate_reviews


def test_product_validation_rejects_negative_price() -> None:
    data = pd.DataFrame(
        {
            "product_id": ["one"],
            "price_cny": [-1.0],
            "sales_lower_bound": [0.0],
            "product_name_zh": ["测试"],
            "seller_name_zh": ["测试店"],
        }
    )
    report = validate_products(data)
    assert not report["passed"]
    assert "price_cny must be positive and non-missing" in report["errors"]


def test_review_validation_accepts_valid_unique_reviews() -> None:
    data = pd.DataFrame(
        {"review_id": ["one", "two"], "review_text_zh": ["好看", "包装好"], "review_length_chars": [2, 3]}
    )
    assert validate_reviews(data)["passed"]

