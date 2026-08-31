from dataclasses import dataclass
from pathlib import Path

import yaml

from src.paths import CONFIG_DIR


@dataclass(frozen=True)
class AnalysisConfig:
    random_seed: int
    price_tiers: dict[str, float]
    sentiment_thresholds: dict[str, float]
    cluster_candidates: tuple[int, ...]
    lda_topic_candidates: tuple[int, ...]
    lda_test_fraction: float
    min_topic_word_document_frequency: int
    max_topic_word_document_fraction: float
    bootstrap_iterations: int


def load_config(path: Path | None = None) -> AnalysisConfig:
    config_path = path or CONFIG_DIR / "analysis.yml"
    values = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return AnalysisConfig(
        random_seed=int(values["random_seed"]),
        price_tiers=values["price_tiers"],
        sentiment_thresholds=values["sentiment_thresholds"],
        cluster_candidates=tuple(values["cluster_candidates"]),
        lda_topic_candidates=tuple(values["lda_topic_candidates"]),
        lda_test_fraction=float(values["lda_test_fraction"]),
        min_topic_word_document_frequency=int(
            values["min_topic_word_document_frequency"]
        ),
        max_topic_word_document_fraction=float(
            values["max_topic_word_document_fraction"]
        ),
        bootstrap_iterations=int(values["bootstrap_iterations"]),
    )

