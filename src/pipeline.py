import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.cleaning import (
    clean_external_products,
    clean_external_reviews,
    clean_products,
    clean_reviews,
)
from src.config import load_config
from src.database import build_database, export_sql_views
from src.evaluation import (
    add_silver_sentiment_labels,
    apply_human_sentiment_labels,
    build_human_aspect_evaluation,
    evaluate_rule_aspects,
    evaluate_sentiment,
    human_adjudication_candidates,
    sentiment_error_cases,
)
from src.external_data import (
    fixed_review_sample,
    read_figshare_reviews,
    read_hooos_product_snapshots,
)
from src.io import (
    read_legacy_products,
    read_legacy_reviews,
    read_legacy_tokens,
    read_legacy_word_frequency,
)
from src.legacy_comparison import compare_legacy_results
from src.paths import (
    EXTERNAL_RAW_DIR,
    INTERIM_DIR,
    OUTPUT_DIR,
    PROCESSED_DIR,
    ROOT,
    ensure_output_directories,
)
from src.segmentation import run_product_segmentation
from src.statistics import product_descriptive_tables, run_product_statistics
from src.text_analysis import (
    build_aspect_summary,
    build_coword_edges,
    build_word_frequency,
    run_lda_topic_model,
    run_text_embedding_clusters,
    score_sentiment,
)
from src.validation import require_valid, validate_products, validate_reviews


def _json_default(value: object) -> object:
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8"
    )


def _write_tables(tables: dict[str, pd.DataFrame], directory: Path) -> None:
    for name, table in tables.items():
        table.to_csv(directory / f"{name}.csv", index=False, encoding="utf-8-sig")


def run_pipeline() -> None:
    ensure_output_directories()
    config = load_config()
    legacy_raw_products = read_legacy_products()
    legacy_raw_reviews = read_legacy_reviews()
    legacy_words = read_legacy_word_frequency()
    legacy_tokens = read_legacy_tokens()

    legacy_products, _ = clean_products(legacy_raw_products, config)
    legacy_reviews, _ = clean_reviews(legacy_raw_reviews)
    raw_products = read_hooos_product_snapshots(EXTERNAL_RAW_DIR / "hooos_museum_blind_box")
    all_external_reviews = read_figshare_reviews(
        EXTERNAL_RAW_DIR / "figshare_30671120" / "Summary of Taobao 8624 Reviews.xlsx"
    )
    raw_reviews = fixed_review_sample(all_external_reviews, size=500, seed=config.random_seed)
    products, product_cleaning_report = clean_external_products(raw_products, config)
    reviews, review_cleaning_report = clean_external_reviews(raw_reviews)
    product_validation = validate_products(products)
    review_validation = validate_reviews(reviews)
    require_valid(product_validation, "products")
    require_valid(review_validation, "reviews")

    products.to_csv(INTERIM_DIR / "products_normalized.csv", index=False, encoding="utf-8-sig")
    reviews.to_csv(INTERIM_DIR / "reviews_normalized.csv", index=False, encoding="utf-8-sig")
    products.to_csv(PROCESSED_DIR / "products_clean.csv", index=False, encoding="utf-8-sig")
    reviews.to_csv(PROCESSED_DIR / "reviews_clean.csv", index=False, encoding="utf-8-sig")

    descriptive = product_descriptive_tables(products)
    regression_coefficients, statistics_summary = run_product_statistics(products)
    cluster_assignments, cluster_evaluation, cluster_profiles, cluster_summary = (
        run_product_segmentation(products, config)
    )
    word_frequency, tokenized = build_word_frequency(reviews)
    lda_evaluation, topics, topic_assignments, lda_summary = run_lda_topic_model(
        reviews, tokenized, config
    )
    embedding_evaluation, embedding_assignments, embedding_summary = run_text_embedding_clusters(
        reviews, config
    )
    scored_reviews, sentiment_summary, sentiment_metadata = score_sentiment(reviews, config)
    evaluation_set = build_human_aspect_evaluation(
        reviews,
        [EXTERNAL_RAW_DIR / "figshare_30671120" / f"Coder {index}.xlsx" for index in range(1, 4)],
        size=180,
        seed=config.random_seed,
    )
    human_annotation_path = ROOT / "data" / "annotations" / "sentiment_human_labels.csv"
    evaluation_set = (
        apply_human_sentiment_labels(evaluation_set, human_annotation_path)
        if human_annotation_path.exists()
        else add_silver_sentiment_labels(evaluation_set)
    )
    sentiment_metrics, sentiment_confusion, sentiment_evaluation = evaluate_sentiment(
        scored_reviews, evaluation_set
    )
    sentiment_errors = sentiment_error_cases(scored_reviews, evaluation_set)
    adjudication_candidates = human_adjudication_candidates(scored_reviews, evaluation_set)
    aspect_evaluation, aspect_evaluation_summary = evaluate_rule_aspects(reviews, evaluation_set)
    sentiment_metadata.update(sentiment_evaluation)
    aspect_summary = build_aspect_summary(scored_reviews)
    coword_edges = build_coword_edges(tokenized)

    cluster_assignments.to_csv(
        PROCESSED_DIR / "products_segmented.csv", index=False, encoding="utf-8-sig"
    )
    scored_reviews.to_csv(
        PROCESSED_DIR / "reviews_scored.csv", index=False, encoding="utf-8-sig"
    )
    topic_assignments.to_csv(
        PROCESSED_DIR / "review_topic_assignments.csv", index=False, encoding="utf-8-sig"
    )
    evaluation_set.to_csv(
        PROCESSED_DIR / "review_evaluation_set.csv", index=False, encoding="utf-8-sig"
    )

    build_database(products, reviews, scored_reviews)
    sql_tables = export_sql_views()
    legacy_comparison = compare_legacy_results(
        legacy_raw_products,
        legacy_raw_reviews,
        legacy_products,
        legacy_reviews,
        sentiment_summary,
        lda_summary,
        cluster_summary,
        legacy_words,
        word_frequency,
    )

    sentiment_shares = sentiment_summary.set_index("sentiment_label")["review_share"].to_dict()
    metric_summary = pd.DataFrame(
        [
            {"metric": "Raw product rows", "value": len(raw_products), "unit": "rows"},
            {"metric": "Clean product listings", "value": len(products), "unit": "listings"},
            {"metric": "Raw review rows", "value": len(raw_reviews), "unit": "rows"},
            {"metric": "Unique clean reviews", "value": len(reviews), "unit": "reviews"},
            {"metric": "Products at or below 100 CNY", "value": int(products["price_cny"].le(100).sum()), "unit": "listings"},
            {"metric": "Median product price", "value": float(products["price_cny"].median()), "unit": "CNY"},
            {"metric": "Claimed-official seller share", "value": float(products["official_store_claimed"].mean()), "unit": "share"},
            {"metric": "Positive SnowNLP share", "value": float(sentiment_shares.get("Positive", 0)), "unit": "share"},
            {"metric": "Negative SnowNLP share", "value": float(sentiment_shares.get("Negative", 0)), "unit": "share"},
            {"metric": "Selected product segments", "value": cluster_summary["selected_cluster_count"], "unit": "clusters"},
            {"metric": "Selected review topics", "value": lda_summary["selected_topic_count"], "unit": "topics"},
        ]
    )
    sample_size_assessment = pd.DataFrame(
        [
            {
                "method": "Exploratory HC3 OLS",
                "sample_size": statistics_summary["sample_size"],
                "rule": ">=10 observations per estimated parameter",
                "observed": statistics_summary["regression_observations_per_parameter"],
                "passed": statistics_summary["regression_sample_size_rule_passed"],
                "decision": "Retained as associational sensitivity analysis",
            },
            {
                "method": "K-Means segmentation",
                "sample_size": cluster_summary["sample_size"],
                "rule": ">=5 products in every selected cluster",
                "observed": cluster_summary["minimum_cluster_size"],
                "passed": cluster_summary["sample_size_rule_passed"],
                "decision": "Retained as exploratory segmentation",
            },
            {
                "method": "LDA topic model",
                "sample_size": lda_summary["sample_size"],
                "rule": ">=20 reviews assigned to every dominant topic",
                "observed": lda_summary["minimum_dominant_topic_documents"],
                "passed": lda_summary["sample_size_rule_passed"],
                "decision": "Retained as exploratory topic model",
            },
            {
                "method": "SnowNLP sentiment classification",
                "sample_size": sentiment_metadata["sample_size"],
                "rule": "Human-labeled validation set required for accuracy claims",
                "observed": sentiment_evaluation["evaluation_rows"],
                "passed": sentiment_evaluation["human_ground_truth"],
                "decision": (
                    "Human-reviewed evaluation completed; Neutral and Mixed pooled for three-class scoring"
                    if sentiment_evaluation["human_ground_truth"]
                    else "Silver-label diagnostic completed; human sentiment audit still required"
                ),
            },
        ]
    )

    output_tables = {
        **descriptive,
        **sql_tables,
        "regression_coefficients": regression_coefficients,
        "cluster_evaluation": cluster_evaluation,
        "cluster_profiles": cluster_profiles,
        "product_cluster_assignments": cluster_assignments,
        "word_frequency": word_frequency,
        "lda_evaluation": lda_evaluation,
        "lda_topics": topics,
        "review_topic_assignments": topic_assignments,
        "embedding_cluster_evaluation": embedding_evaluation,
        "review_embedding_assignments": embedding_assignments,
        "sentiment_summary": sentiment_summary,
        "reviews_scored": scored_reviews,
        "review_evaluation_set": evaluation_set,
        "sentiment_evaluation_metrics": sentiment_metrics,
        "sentiment_confusion_matrix": sentiment_confusion,
        "sentiment_error_cases": sentiment_errors,
        "human_adjudication_candidates": adjudication_candidates,
        "aspect_evaluation_metrics": aspect_evaluation,
        "aspect_summary": aspect_summary,
        "coword_edges": coword_edges,
        "legacy_comparison": legacy_comparison,
        "metric_summary": metric_summary,
        "sample_size_assessment": sample_size_assessment,
    }
    _write_tables(output_tables, OUTPUT_DIR)

    quality_report = {
        "product_cleaning": product_cleaning_report,
        "review_cleaning": review_cleaning_report,
        "product_validation": product_validation,
        "review_validation": review_validation,
        "legacy_word_frequency_rows": len(legacy_words),
        "legacy_token_rows": len(legacy_tokens),
    }
    model_report = {
        "configuration": asdict(config),
        "statistics": statistics_summary,
        "segmentation": cluster_summary,
        "lda": lda_summary,
        "embedding_clustering": embedding_summary,
        "sentiment": sentiment_metadata,
        "aspect_evaluation": aspect_evaluation_summary,
    }
    _write_json(OUTPUT_DIR / "data_quality_report.json", quality_report)
    _write_json(OUTPUT_DIR / "model_report.json", model_report)
    print("Pipeline completed successfully.")
    print(f"Clean products: {len(products)}")
    print(f"Clean reviews: {len(reviews)}")
    print(f"Selected clusters: {cluster_summary['selected_cluster_count']}")
    print(f"Selected LDA topics: {lda_summary['selected_topic_count']}")


if __name__ == "__main__":
    run_pipeline()
