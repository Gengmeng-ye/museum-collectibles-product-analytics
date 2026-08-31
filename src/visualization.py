from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from src.paths import OUTPUT_DIR, ROOT

FIGURE_DIR = ROOT / "reports" / "figures"
COLORS = ["#F28A73", "#FFC847", "#4EB6D8", "#F7A8B8", "#8F88D8", "#7ECFC6"]


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#A9B0B4",
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "font.size": 9,
            "grid.color": "#DDE2E5",
            "grid.linewidth": 0.7,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def _save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIGURE_DIR / name, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_price_and_tiers(products: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].hist(products["price_cny"], bins=[0, 25, 50, 75, 100, 150, 200, 700], color=COLORS[2], edgecolor="white")
    axes[0].axvline(products["price_cny"].median(), color=COLORS[0], linestyle="--", label=f"Median: CNY {products['price_cny'].median():.0f}")
    axes[0].set(title="Product price distribution", xlabel="Displayed price (CNY)", ylabel="Listings")
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y")

    order = ["Budget (<=50 CNY)", "Mass Market (51-100 CNY)", "Premium (101-200 CNY)", "High-end (>200 CNY)"]
    counts = products["price_tier"].value_counts().reindex(order, fill_value=0)
    labels = ["Budget", "Mass market", "Premium", "High-end"]
    bars = axes[1].bar(labels, counts, color=COLORS[:4])
    axes[1].bar_label(bars, padding=3)
    axes[1].set(title="Assortment by price tier", xlabel="Price tier", ylabel="Listings")
    axes[1].grid(axis="y")
    fig.suptitle("Museum blind-box assortment is concentrated below CNY 100", fontsize=15, fontweight="bold")
    _save(fig, "01-price-and-tier-distribution.png")


def plot_assortment(products: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw={"wspace": 0.42})
    for axis, column, title in [
        (axes[0], "product_category", "Product category"),
        (axes[1], "product_format", "Product format"),
    ]:
        counts = products[column].replace({"Other Blind-box Format": "Other format"}).value_counts().sort_values()
        bars = axis.barh(counts.index, counts.values, color=COLORS[2])
        axis.bar_label(bars, padding=3)
        axis.set(title=title, xlabel="Listings", ylabel="")
        axis.grid(axis="x")
    fig.suptitle("The indexed assortment is dominated by figurines and excavation kits", fontsize=15, fontweight="bold")
    _save(fig, "02-assortment-mix.png")


def plot_k_selection(evaluation: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    ax.plot(evaluation["cluster_count"], evaluation["silhouette_score"], marker="o", color=COLORS[0], label="Silhouette")
    ax.set(xlabel="Number of clusters (K)", ylabel="Silhouette score", title="K=5 balances separation and bootstrap stability")
    ax.grid()
    second = ax.twinx()
    second.plot(evaluation["cluster_count"], evaluation["bootstrap_adjusted_rand_mean"], marker="s", color=COLORS[1], label="Bootstrap ARI")
    second.set_ylabel("Bootstrap adjusted Rand index")
    selected = evaluation.loc[evaluation["selection_score"].idxmax()]
    ax.axvline(selected["cluster_count"], color="#5F6B6D", linestyle="--", linewidth=1)
    lines = ax.get_lines()[:1] + second.get_lines()[:1]
    ax.legend(lines, [line.get_label() for line in lines], frameon=False, loc="lower right")
    _save(fig, "03-kmeans-model-selection.png")


def plot_cluster_profiles(profiles: pd.DataFrame) -> None:
    profile = profiles.set_index("interpreted_cluster_label")
    values = pd.DataFrame(
        {
            "Median price": profile["median_price_cny"],
            "Official-store share": profile["claimed_official_share"] * 100,
            "Museum/IP share": profile["museum_ip_share"] * 100,
            "Sales coverage": profile["sales_coverage"] * 100,
        }
    )
    normalized = (values - values.min()) / (values.max() - values.min()).replace(0, 1)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    pastel_map = LinearSegmentedColormap.from_list(
        "collectible_pastel", ["#FFF8F3", "#F7A8B8", "#8F88D8", "#4EB6D8"]
    )
    image = ax.imshow(normalized.values, cmap=pastel_map, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(values.columns)), values.columns, rotation=20, ha="right")
    ax.set_yticks(range(len(values.index)), values.index)
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            suffix = " CNY" if column == 0 else "%"
            text_color = "white" if normalized.iloc[row, column] >= 0.62 else "black"
            ax.text(column, row, f"{values.iloc[row, column]:.0f}{suffix}", ha="center", va="center", color=text_color)
    ax.set_title("Five exploratory product segments show distinct commercial profiles")
    fig.colorbar(image, ax=ax, label="Within-metric relative level", shrink=0.8)
    _save(fig, "04-segment-profile-heatmap.png")


def plot_topic_selection(evaluation: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
    axes[0].plot(evaluation["topic_count"], evaluation["heldout_perplexity"], marker="o", color=COLORS[0])
    axes[0].set(title="Held-out perplexity", xlabel="Number of topics", ylabel="Lower is better")
    axes[0].grid()
    axes[1].plot(evaluation["topic_count"], evaluation["topic_diversity_top10"], marker="o", label="Diversity", color=COLORS[2])
    axes[1].plot(evaluation["topic_count"], evaluation["topic_separation_top10"], marker="s", label="Separation", color=COLORS[1])
    axes[1].set(title="Top-word diagnostics", xlabel="Number of topics", ylabel="Score")
    axes[1].legend(frameon=False)
    axes[1].grid()
    fig.suptitle("Two broad LDA topics outperform more fragmented solutions", fontsize=15, fontweight="bold")
    _save(fig, "05-lda-model-selection.png")


def plot_sentiment_diagnostics(summary: pd.DataFrame, confusion: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.4), gridspec_kw={"wspace": 0.32})
    order = ["Negative", "Neutral / Mixed", "Positive"]
    shares = summary.set_index("sentiment_label")["review_share"].reindex(order, fill_value=0) * 100
    bars = axes[0].bar(order, shares, color=[COLORS[1], COLORS[5], COLORS[2]])
    axes[0].bar_label(bars, labels=[f"{value:.1f}%" for value in shares], padding=3)
    axes[0].set(title="SnowNLP output distribution", xlabel="Predicted label", ylabel="Reviews (%)")
    axes[0].tick_params(axis="x", rotation=15)
    axes[0].grid(axis="y")

    matrix = confusion.set_index("actual_label").to_numpy()
    image = axes[1].imshow(matrix, cmap="Blues")
    axes[1].set_xticks(range(3), order, rotation=20, ha="right")
    axes[1].set_yticks(range(3), order)
    axes[1].set(xlabel="SnowNLP prediction", ylabel="", title="Diagnostic confusion matrix")
    for row in range(3):
        for column in range(3):
            axes[1].text(column, row, int(matrix[row, column]), ha="center", va="center")
    fig.colorbar(image, ax=axes[1], shrink=0.75)
    fig.suptitle("SnowNLP over-predicts positive sentiment in ambiguous reviews", fontsize=15, fontweight="bold")
    _save(fig, "06-sentiment-diagnostics.png")


def plot_aspect_evaluation(metrics: pd.DataFrame) -> None:
    data = metrics.sort_values("f1")
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    bars = ax.barh(data["aspect"], data["f1"], color=[COLORS[0] if value < 0.6 else COLORS[2] for value in data["f1"]])
    ax.bar_label(bars, labels=[f"F1 {value:.2f}" for value in data["f1"]], padding=3)
    for position, support in enumerate(data["support"]):
        ax.text(0.02, position, f"n={support}", va="center", color="white" if data.iloc[position]["f1"] > 0.2 else "black")
    ax.set(xlim=(0, 1.08), xlabel="F1 against human-coded aspects", ylabel="", title="Rule-based aspect extraction is reliable only for selected aspects")
    ax.grid(axis="x")
    _save(fig, "07-aspect-model-evaluation.png")


def build_all_figures() -> list[Path]:
    _style()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    products = pd.read_csv(OUTPUT_DIR / "product_cluster_assignments.csv")
    plot_price_and_tiers(products)
    plot_assortment(products)
    plot_k_selection(pd.read_csv(OUTPUT_DIR / "cluster_evaluation.csv"))
    plot_cluster_profiles(pd.read_csv(OUTPUT_DIR / "cluster_profiles.csv"))
    plot_topic_selection(pd.read_csv(OUTPUT_DIR / "lda_evaluation.csv"))
    plot_sentiment_diagnostics(
        pd.read_csv(OUTPUT_DIR / "sentiment_summary.csv"),
        pd.read_csv(OUTPUT_DIR / "sentiment_confusion_matrix.csv"),
    )
    plot_aspect_evaluation(pd.read_csv(OUTPUT_DIR / "aspect_evaluation_metrics.csv"))
    return sorted(FIGURE_DIR.glob("*.png"))


if __name__ == "__main__":
    files = build_all_figures()
    print(f"Created {len(files)} figures in {FIGURE_DIR}")
