import pandas as pd


def compare_legacy_results(
    raw_products: pd.DataFrame,
    raw_reviews: pd.DataFrame,
    clean_products: pd.DataFrame,
    clean_reviews: pd.DataFrame,
    sentiment_summary: pd.DataFrame,
    lda_summary: dict,
    cluster_summary: dict,
    legacy_word_frequency: pd.DataFrame,
    new_word_frequency: pd.DataFrame,
) -> pd.DataFrame:
    shares = sentiment_summary.set_index("sentiment_label")["review_share"].to_dict()
    legacy_terms = set(legacy_word_frequency.iloc[:, 0].astype(str))
    new_top_terms = set(new_word_frequency.head(25)["term"].astype(str))
    overlap = sorted(legacy_terms & new_top_terms)
    rows = [
        {
            "legacy_claim": "50 products collected",
            "new_result": f"{len(raw_products)} retained rows; {len(clean_products)} after exact deduplication",
            "status": "Not reproduced",
            "reason": "The retained workbook contains fewer rows than the report states.",
        },
        {
            "legacy_claim": "120 valid reviews collected",
            "new_result": f"{len(raw_reviews)} retained rows; {len(clean_reviews)} unique reviews",
            "status": "Not reproduced",
            "reason": "The retained workbook contains 100 rows including duplicates.",
        },
        {
            "legacy_claim": "Most product prices are below 100 CNY",
            "new_result": f"{int(clean_products['price_cny'].le(100).sum())}/{len(clean_products)} ({clean_products['price_cny'].le(100).mean():.1%})",
            "status": "Reproduced descriptively",
            "reason": "Directly calculated from retained listing prices.",
        },
        {
            "legacy_claim": "Legacy high-frequency review terms",
            "new_result": f"{len(overlap)}/{len(legacy_terms)} retained legacy terms overlap the new top 25: {' / '.join(overlap)}",
            "status": "Partially reproduced",
            "reason": "The expanded review sample uses a versioned tokenizer and stopword list.",
        },
        {
            "legacy_claim": "K-Means with k=2 separates authentic and counterfeit products",
            "new_result": f"Selected k={cluster_summary['selected_cluster_count']} using silhouette and stability",
            "status": "Legacy interpretation rejected",
            "reason": "No verified authenticity label exists; clusters are exploratory product segments.",
        },
        {
            "legacy_claim": "Six LDA topics are optimal",
            "new_result": f"Selected {lda_summary['selected_topic_count']} topics using held-out perplexity, coherence, diversity, and separation",
            "status": "Re-estimated",
            "reason": "The legacy coherence code treated individual terms as documents and the modeling input is missing.",
        },
        {
            "legacy_claim": "Sentiment is 47% positive, 31% negative, and 22% neutral",
            "new_result": (
                f"Positive {shares.get('Positive', 0):.1%}; Negative {shares.get('Negative', 0):.1%}; "
                f"Neutral/Mixed {shares.get('Neutral / Mixed', 0):.1%}"
            ),
            "status": "Not exactly reproduced",
            "reason": "Legacy thresholds were not documented; the expanded sample and explicit thresholds change the distribution.",
        },
        {
            "legacy_claim": "Museum-level sales and revenue shares",
            "new_result": "Only displayed sales lower bounds can be aggregated",
            "status": "Revenue result rejected",
            "reason": "Only 78/150 expanded listings display sales, so market revenue shares would be misleading.",
        },
    ]
    return pd.DataFrame(rows)
