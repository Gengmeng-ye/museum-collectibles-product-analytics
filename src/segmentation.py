import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import AnalysisConfig

NUMERIC_FEATURES = ["log_price_cny", "log_sales_lower_bound", "title_length_chars"]
CATEGORICAL_FEATURES = ["official_store_claimed", "museum_ip_flag", "product_category", "product_format"]
KEYWORD_FEATURES = ["keyword_excavation", "keyword_gift", "keyword_collectible", "sales_observed"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES + KEYWORD_FEATURES


def _feature_matrix(products: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, ColumnTransformer]:
    features = pd.DataFrame(
        {
            "log_price_cny": np.log1p(products["price_cny"]),
            "log_sales_lower_bound": np.log1p(products["sales_lower_bound"]),
            "title_length_chars": products["title_length_chars"].astype(float),
            "official_store_claimed": products["official_store_claimed"].astype(float),
            "museum_ip_flag": products["museum_ip_flag"].astype(float),
            "product_category": products["product_category"],
            "product_format": products["product_format"],
            "keyword_excavation": products["keyword_excavation"].astype(float),
            "keyword_gift": products["keyword_gift"].astype(float),
            "keyword_collectible": products["keyword_collectible"].astype(float),
            "sales_observed": products["sales_observed"].astype(float),
        },
        index=products.index,
    )
    transformer = ColumnTransformer(
        [
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
            ("keywords", "passthrough", KEYWORD_FEATURES),
        ]
    )
    scaled = transformer.fit_transform(features)
    return features, scaled, transformer


def _bootstrap_stability(
    scaled: np.ndarray, k: int, config: AnalysisConfig
) -> tuple[float, float]:
    rng = np.random.default_rng(config.random_seed)
    full_model = KMeans(n_clusters=k, n_init=25, random_state=config.random_seed).fit(scaled)
    scores: list[float] = []
    sample_size = max(k * 3, int(len(scaled) * 0.8))
    for iteration in range(config.bootstrap_iterations):
        indices = np.sort(rng.choice(len(scaled), size=sample_size, replace=False))
        model = KMeans(
            n_clusters=k, n_init=15, random_state=config.random_seed + iteration + 1
        ).fit(scaled[indices])
        scores.append(adjusted_rand_score(full_model.labels_[indices], model.labels_))
    return float(np.mean(scores)), float(np.std(scores, ddof=1))


def run_product_segmentation(
    products: pd.DataFrame, config: AnalysisConfig
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    _, scaled, _ = _feature_matrix(products)
    valid_candidates = [k for k in config.cluster_candidates if 2 <= k < len(products)]
    evaluation_rows: list[dict] = []
    for k in valid_candidates:
        model = KMeans(n_clusters=k, n_init=25, random_state=config.random_seed).fit(scaled)
        stability_mean, stability_std = _bootstrap_stability(scaled, k, config)
        minimum_cluster_size = int(np.bincount(model.labels_).min())
        evaluation_rows.append(
            {
                "cluster_count": k,
                "inertia": float(model.inertia_),
                "silhouette_score": float(silhouette_score(scaled, model.labels_)),
                "bootstrap_adjusted_rand_mean": stability_mean,
                "bootstrap_adjusted_rand_std": stability_std,
                "minimum_cluster_size": minimum_cluster_size,
                "sample_size_rule_passed": minimum_cluster_size >= 5,
            }
        )
    evaluation = pd.DataFrame(evaluation_rows)
    evaluation["selection_score"] = (
        evaluation["silhouette_score"] * evaluation["bootstrap_adjusted_rand_mean"]
    )
    eligible = evaluation.loc[evaluation["sample_size_rule_passed"]]
    if eligible.empty:
        eligible = evaluation
    selected_k = int(
        eligible.sort_values(
            ["selection_score", "silhouette_score"], ascending=False
        ).iloc[0]["cluster_count"]
    )
    final_model = KMeans(
        n_clusters=selected_k, n_init=50, random_state=config.random_seed
    ).fit(scaled)
    assignments = products.copy()
    assignments["cluster_id"] = final_model.labels_ + 1
    profile = (
        assignments.groupby("cluster_id")
        .agg(
            product_count=("product_id", "count"),
            median_price_cny=("price_cny", "median"),
            median_sales_lower_bound=("sales_lower_bound", "median"),
            claimed_official_share=("official_store_claimed", "mean"),
            median_title_length=("title_length_chars", "median"),
            museum_ip_share=("museum_ip_flag", "mean"),
            sales_coverage=("sales_observed", "mean"),
        )
        .reset_index()
    )
    modes = (
        assignments.groupby("cluster_id")
        .agg(
            dominant_category=("product_category", lambda values: values.mode().iat[0]),
            dominant_format=("product_format", lambda values: values.mode().iat[0]),
            dominant_museum=("museum_name", lambda values: values.mode().iat[0]),
        )
        .reset_index()
    )
    profile = profile.merge(modes, on="cluster_id")

    def interpret(row: pd.Series) -> str:
        if row["dominant_category"] == "Excavation Kit":
            return (
                "Official museum excavation kits"
                if row["claimed_official_share"] >= 0.5
                else "Budget marketplace excavation kits"
            )
        if row["sales_coverage"] >= 0.8:
            return "Sales-visible character collectibles"
        if row["median_price_cny"] >= 65:
            return "Premium museum figurines"
        return "Broad museum collectible assortment"

    profile["interpreted_cluster_label"] = profile.apply(interpret, axis=1)
    assignments = assignments.merge(
        profile[["cluster_id", "interpreted_cluster_label"]], on="cluster_id", how="left"
    )
    summary = {
        "selected_cluster_count": selected_k,
        "selection_rule": (
            "Maximum silhouette score multiplied by bootstrap ARI stability, restricted to "
            "solutions with at least five products in every cluster."
        ),
        "sample_size": len(products),
        "features": FEATURE_COLUMNS,
        "exploratory_only": True,
        "minimum_cluster_size": int(assignments["cluster_id"].value_counts().min()),
        "sample_size_rule_passed": bool(
            assignments["cluster_id"].value_counts().min() >= 5
        ),
    }
    return assignments, evaluation, profile, summary
