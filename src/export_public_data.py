"""Export privacy-conscious public datasets from generated pipeline outputs."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

from src.paths import ROOT


PUBLIC_DIR = ROOT / "data" / "public"
AGGREGATE_DIR = PUBLIC_DIR / "aggregates"

PRODUCT_FIELDS = [
    "product_id",
    "source_platform",
    "collection_date",
    "price_cny",
    "sales_lower_bound",
    "sales_is_censored",
    "sales_observed",
    "official_store_claimed",
    "museum_name",
    "museum_ip_flag",
    "product_category",
    "product_format",
    "price_tier",
    "title_length_chars",
    "keyword_excavation",
    "keyword_gift",
    "keyword_collectible",
    "cluster_id",
    "interpreted_cluster_label",
]

REVIEW_FIELDS = [
    "review_id",
    "review_length_chars",
    "aspects",
    "aspect_count",
    "sentiment_score",
    "sentiment_label",
    "dominant_topic_id",
    "dominant_topic_probability",
    "topic_1_probability",
    "topic_2_probability",
    "topic_label",
]

EVALUATION_FIELDS = [
    "review_id",
    "manual_aspects",
    "manual_sentiment",
    "is_adjudicated",
    "reference_sentiment",
    "sentiment_label",
    "sentiment_score",
]

AGGREGATE_FILES = [
    "aspect_evaluation_metrics.csv",
    "category_summary.csv",
    "cluster_evaluation.csv",
    "cluster_profiles.csv",
    "lda_evaluation.csv",
    "lda_topics.csv",
    "price_tier_summary.csv",
    "sample_size_assessment.csv",
    "sentiment_confusion_matrix.csv",
    "sentiment_evaluation_metrics.csv",
    "sentiment_summary.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_subset(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    missing = set(fields) - set(rows[0])
    if missing:
        raise ValueError(f"Missing fields for {path.name}: {sorted(missing)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)


def export_products() -> None:
    rows = read_csv(ROOT / "data" / "processed" / "products_segmented.csv")
    write_subset(PUBLIC_DIR / "products_anonymized.csv", rows, PRODUCT_FIELDS)


def export_reviews() -> None:
    scored = read_csv(ROOT / "data" / "processed" / "reviews_scored.csv")
    topics = {
        row["review_id"]: row
        for row in read_csv(ROOT / "data" / "processed" / "review_topic_assignments.csv")
    }
    rows = [{**row, **topics[row["review_id"]]} for row in scored]
    write_subset(PUBLIC_DIR / "review_model_outputs_anonymized.csv", rows, REVIEW_FIELDS)


def export_evaluation() -> None:
    evaluation = read_csv(ROOT / "data" / "processed" / "review_evaluation_set.csv")
    scored = {
        row["review_id"]: row
        for row in read_csv(ROOT / "data" / "processed" / "reviews_scored.csv")
    }
    rows = [{**row, **scored[row["review_id"]]} for row in evaluation]
    write_subset(PUBLIC_DIR / "sentiment_evaluation_anonymized.csv", rows, EVALUATION_FIELDS)


def export_aggregates() -> None:
    AGGREGATE_DIR.mkdir(parents=True, exist_ok=True)
    for filename in AGGREGATE_FILES:
        shutil.copyfile(ROOT / "outputs" / filename, AGGREGATE_DIR / filename)


def main() -> None:
    export_products()
    export_reviews()
    export_evaluation()
    export_aggregates()


if __name__ == "__main__":
    main()
