import pandas as pd


def validate_products(data: pd.DataFrame) -> dict:
    errors: list[str] = []
    if data["product_id"].duplicated().any():
        errors.append("product_id must be unique")
    if data["price_cny"].isna().any() or data["price_cny"].le(0).any():
        errors.append("price_cny must be positive and non-missing")
    if data["sales_lower_bound"].dropna().lt(0).any():
        errors.append("observed sales_lower_bound values must be non-negative")
    if data["product_name_zh"].eq("").any():
        errors.append("product_name_zh must be non-empty")
    if data["seller_name_zh"].eq("").any():
        errors.append("seller_name_zh must be non-empty")
    return {"passed": not errors, "errors": errors, "row_count": len(data)}


def validate_reviews(data: pd.DataFrame) -> dict:
    errors: list[str] = []
    if data["review_id"].duplicated().any():
        errors.append("review_id must be unique")
    if data["review_text_zh"].eq("").any():
        errors.append("review_text_zh must be non-empty")
    if data["review_length_chars"].lt(1).any():
        errors.append("review_length_chars must be positive")
    return {"passed": not errors, "errors": errors, "row_count": len(data)}


def require_valid(report: dict, dataset_name: str) -> None:
    if not report["passed"]:
        raise ValueError(f"{dataset_name} validation failed: {report['errors']}")
