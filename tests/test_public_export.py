import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "data"


def read_rows(filename: str) -> list[dict[str, str]]:
    with (PUBLIC / filename).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_public_export_row_counts() -> None:
    assert len(read_rows("products.csv")) == 150
    assert len(read_rows("reviews.csv")) == 500
    assert len(read_rows("sentiment_evaluation.csv")) == 180


def test_public_export_excludes_sensitive_columns() -> None:
    forbidden = {
        "product_name_zh",
        "seller_name_zh",
        "source_url",
        "review_text_zh",
        "reviewer_id",
        "review_notes",
    }
    for filename in (
        "products.csv",
        "reviews.csv",
        "sentiment_evaluation.csv",
    ):
        rows = read_rows(filename)
        assert rows
        assert forbidden.isdisjoint(rows[0])
