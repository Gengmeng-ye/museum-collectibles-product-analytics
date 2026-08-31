import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


def _rank_biserial_from_u(u_statistic: float, n_one: int, n_two: int) -> float:
    return 2 * u_statistic / (n_one * n_two) - 1


def run_product_statistics(products: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    data = products.copy()
    official = data.loc[data["official_store_claimed"], "price_cny"]
    other = data.loc[~data["official_store_claimed"], "price_cny"]
    u_result = stats.mannwhitneyu(official, other, alternative="two-sided")
    sales_observed = data.dropna(subset=["price_cny", "sales_lower_bound"]).copy()
    spearman = stats.spearmanr(sales_observed["price_cny"], sales_observed["sales_lower_bound"])

    regression_frame = pd.DataFrame(
        {
            "log_sales_lower_bound": np.log1p(sales_observed["sales_lower_bound"]),
            "log_price_cny": np.log1p(sales_observed["price_cny"]),
            "official_store_claimed": sales_observed["official_store_claimed"].astype(int),
        }
    )
    design = sm.add_constant(regression_frame[["log_price_cny", "official_store_claimed"]])
    model = sm.OLS(regression_frame["log_sales_lower_bound"], design).fit(cov_type="HC3")
    confidence = model.conf_int(alpha=0.05)
    coefficient_table = pd.DataFrame(
        {
            "term": model.params.index,
            "coefficient": model.params.values,
            "robust_standard_error": model.bse.values,
            "p_value": model.pvalues.values,
            "confidence_interval_low": confidence[0].values,
            "confidence_interval_high": confidence[1].values,
        }
    )

    observations_per_parameter = len(regression_frame) / len(model.params)
    summary = {
        "sample_size": len(data),
        "sales_observed_sample_size": len(sales_observed),
        "official_store_claimed_count": int(data["official_store_claimed"].sum()),
        "other_store_count": int((~data["official_store_claimed"]).sum()),
        "official_price_median_cny": float(official.median()),
        "other_price_median_cny": float(other.median()),
        "mann_whitney_u": float(u_result.statistic),
        "mann_whitney_p_value": float(u_result.pvalue),
        "price_rank_biserial_effect": float(
            _rank_biserial_from_u(u_result.statistic, len(official), len(other))
        ),
        "price_sales_spearman_rho": float(spearman.statistic),
        "price_sales_spearman_p_value": float(spearman.pvalue),
        "regression_r_squared": float(model.rsquared),
        "regression_adjusted_r_squared": float(model.rsquared_adj),
        "regression_observations_per_parameter": float(observations_per_parameter),
        "regression_sample_size_rule_passed": bool(observations_per_parameter >= 10),
        "interpretation_constraint": (
            "Displayed sales are censored lower bounds; all estimates are exploratory associations."
        ),
    }
    return coefficient_table, summary


def product_descriptive_tables(products: pd.DataFrame) -> dict[str, pd.DataFrame]:
    category = (
        products.groupby("product_category", dropna=False)
        .agg(
            product_count=("product_id", "count"),
            median_price_cny=("price_cny", "median"),
            average_price_cny=("price_cny", "mean"),
            displayed_sales_lower_bound=("sales_lower_bound", "sum"),
        )
        .reset_index()
    )
    category["product_share"] = category["product_count"] / len(products)
    category = category.sort_values("product_count", ascending=False)

    price_tier = (
        products.groupby("price_tier", dropna=False)
        .agg(
            product_count=("product_id", "count"),
            displayed_sales_lower_bound=("sales_lower_bound", "sum"),
            claimed_official_share=("official_store_claimed", "mean"),
        )
        .reset_index()
    )
    price_tier["product_share"] = price_tier["product_count"] / len(products)

    museum = (
        products.groupby("museum_name", dropna=False)
        .agg(
            product_count=("product_id", "count"),
            median_price_cny=("price_cny", "median"),
            displayed_sales_lower_bound=("sales_lower_bound", "sum"),
        )
        .reset_index()
        .sort_values("product_count", ascending=False)
    )
    return {"category_summary": category, "price_tier_summary": price_tier, "museum_summary": museum}
