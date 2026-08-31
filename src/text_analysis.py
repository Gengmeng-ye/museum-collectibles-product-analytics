from collections import Counter
from pathlib import Path

import jieba
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
from snownlp import SnowNLP

from src.config import AnalysisConfig
from src.paths import CONFIG_DIR


def load_stopwords(path: Path | None = None) -> set[str]:
    stopword_path = path or CONFIG_DIR / "stopwords_zh.txt"
    return {
        line.strip()
        for line in stopword_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def tokenize_chinese(text: str, stopwords: set[str]) -> list[str]:
    return [
        token.strip().lower()
        for token in jieba.lcut(text, cut_all=False)
        if len(token.strip()) > 1
        and token.strip() not in stopwords
        and any(character.isalnum() or "\u4e00" <= character <= "\u9fff" for character in token)
    ]


def build_word_frequency(reviews: pd.DataFrame) -> tuple[pd.DataFrame, list[list[str]]]:
    stopwords = load_stopwords()
    tokenized = [tokenize_chinese(text, stopwords) for text in reviews["review_text_zh"]]
    token_counts = Counter(token for document in tokenized for token in document)
    document_counts = Counter(token for document in tokenized for token in set(document))
    total_tokens = sum(token_counts.values())
    rows = [
        {
            "term": term,
            "term_count": count,
            "document_count": document_counts[term],
            "term_frequency": count / total_tokens if total_tokens else 0,
        }
        for term, count in token_counts.most_common()
    ]
    return pd.DataFrame(rows), tokenized


def _topic_diversity(components: np.ndarray, top_n: int = 10) -> float:
    top_indices = [set(topic.argsort()[-top_n:]) for topic in components]
    unique_words = len(set().union(*top_indices))
    return unique_words / (len(top_indices) * top_n)


def _topic_separation(components: np.ndarray, top_n: int = 10) -> float:
    top_sets = [set(topic.argsort()[-top_n:]) for topic in components]
    overlaps: list[float] = []
    for left in range(len(top_sets)):
        for right in range(left + 1, len(top_sets)):
            union = top_sets[left] | top_sets[right]
            overlaps.append(len(top_sets[left] & top_sets[right]) / len(union))
    return 1 - float(np.mean(overlaps)) if overlaps else 1.0


def _umass_coherence(components: np.ndarray, matrix, top_n: int = 10) -> float:
    binary = matrix.astype(bool).astype(int)
    scores: list[float] = []
    for component in components:
        indices = component.argsort()[-top_n:][::-1]
        for later in range(1, len(indices)):
            for earlier in range(later):
                word_later = indices[later]
                word_earlier = indices[earlier]
                co_docs = binary[:, word_later].multiply(binary[:, word_earlier]).sum()
                earlier_docs = binary[:, word_earlier].sum()
                scores.append(float(np.log((co_docs + 1) / max(earlier_docs, 1))))
    return float(np.mean(scores)) if scores else float("nan")


def run_lda_topic_model(
    reviews: pd.DataFrame, tokenized: list[list[str]], config: AnalysisConfig
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    documents = [" ".join(tokens) for tokens in tokenized]
    train_indices, test_indices = train_test_split(
        np.arange(len(documents)),
        test_size=config.lda_test_fraction,
        random_state=config.random_seed,
    )
    vectorizer = CountVectorizer(
        tokenizer=str.split,
        token_pattern=None,
        min_df=config.min_topic_word_document_frequency,
        max_df=config.max_topic_word_document_fraction,
    )
    train_matrix = vectorizer.fit_transform([documents[index] for index in train_indices])
    test_matrix = vectorizer.transform([documents[index] for index in test_indices])
    full_matrix = vectorizer.transform(documents)
    terms = np.asarray(vectorizer.get_feature_names_out())

    evaluations: list[dict] = []
    models: dict[int, LatentDirichletAllocation] = {}
    for topic_count in config.lda_topic_candidates:
        model = LatentDirichletAllocation(
            n_components=topic_count,
            learning_method="batch",
            max_iter=100,
            random_state=config.random_seed,
        ).fit(train_matrix)
        models[topic_count] = model
        evaluations.append(
            {
                "topic_count": topic_count,
                "heldout_perplexity": float(model.perplexity(test_matrix)),
                "topic_diversity_top10": _topic_diversity(model.components_),
                "topic_separation_top10": _topic_separation(model.components_),
                "umass_coherence_top10": _umass_coherence(model.components_, train_matrix),
            }
        )
    evaluation = pd.DataFrame(evaluations)
    for column in ("heldout_perplexity",):
        minimum, maximum = evaluation[column].min(), evaluation[column].max()
        evaluation[f"{column}_normalized"] = (
            (evaluation[column] - minimum) / (maximum - minimum) if maximum > minimum else 0.0
        )
    evaluation["selection_score"] = (
        0.45 * (1 - evaluation["heldout_perplexity_normalized"])
        + 0.30 * evaluation["topic_diversity_top10"]
        + 0.25 * evaluation["topic_separation_top10"]
    )
    selected_topics = int(
        evaluation.sort_values("selection_score", ascending=False).iloc[0]["topic_count"]
    )
    final_model = LatentDirichletAllocation(
        n_components=selected_topics,
        learning_method="batch",
        max_iter=100,
        random_state=config.random_seed,
    ).fit(full_matrix)
    distributions = final_model.transform(full_matrix)

    topic_rows: list[dict] = []
    for topic_index, component in enumerate(final_model.components_, start=1):
        indices = component.argsort()[-15:][::-1]
        weights = component[indices] / component.sum()
        topic_rows.append(
            {
                "topic_id": topic_index,
                "topic_label": " / ".join(terms[indices[:3]]),
                "top_terms": "|".join(terms[indices]),
                "top_term_weights": "|".join(f"{weight:.6f}" for weight in weights),
            }
        )
    topics = pd.DataFrame(topic_rows)
    assignments = reviews[["review_id", "review_text_zh"]].copy()
    assignments["dominant_topic_id"] = distributions.argmax(axis=1) + 1
    assignments["dominant_topic_probability"] = distributions.max(axis=1)
    for index in range(selected_topics):
        assignments[f"topic_{index + 1}_probability"] = distributions[:, index]
    assignments = assignments.merge(topics[["topic_id", "topic_label"]], left_on="dominant_topic_id", right_on="topic_id").drop(columns="topic_id")

    minimum_topic_documents = int(assignments["dominant_topic_id"].value_counts().min())

    summary = {
        "sample_size": len(reviews),
        "training_documents": len(train_indices),
        "heldout_documents": len(test_indices),
        "vocabulary_size": len(terms),
        "selected_topic_count": selected_topics,
        "selection_rule": "Weighted held-out perplexity, top-word diversity, and separation.",
        "exploratory_only": True,
        "minimum_dominant_topic_documents": minimum_topic_documents,
        "sample_size_rule_passed": minimum_topic_documents >= 20,
    }
    return evaluation, topics, assignments, summary


def score_sentiment(
    reviews: pd.DataFrame, config: AnalysisConfig
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    scored = reviews.copy()
    scored["sentiment_score"] = scored["review_text_zh"].map(lambda text: float(SnowNLP(text).sentiments))
    thresholds = config.sentiment_thresholds

    def label(score: float) -> str:
        if score <= thresholds["negative_max"]:
            return "Negative"
        if score >= thresholds["positive_min"]:
            return "Positive"
        return "Neutral / Mixed"

    scored["sentiment_label"] = scored["sentiment_score"].map(label)
    summary_table = (
        scored.groupby("sentiment_label")
        .agg(review_count=("review_id", "count"), average_score=("sentiment_score", "mean"))
        .reset_index()
    )
    summary_table["review_share"] = summary_table["review_count"] / len(scored)
    summary = {
        "sample_size": len(scored),
        "negative_max_threshold": thresholds["negative_max"],
        "positive_min_threshold": thresholds["positive_min"],
        "has_human_labeled_validation_set": False,
        "accuracy_claim_supported": False,
    }
    return scored, summary_table, summary


def build_aspect_summary(scored_reviews: pd.DataFrame) -> pd.DataFrame:
    exploded = scored_reviews.assign(aspect=scored_reviews["aspects"].str.split("|"))
    exploded = exploded.explode("aspect")
    exploded = exploded.loc[exploded["aspect"].fillna("").ne("")]
    summary = (
        exploded.groupby("aspect")
        .agg(
            review_count=("review_id", "nunique"),
            average_sentiment_score=("sentiment_score", "mean"),
            negative_review_count=("sentiment_label", lambda values: int((values == "Negative").sum())),
        )
        .reset_index()
    )
    summary["negative_review_share"] = summary["negative_review_count"] / summary["review_count"]
    return summary.sort_values("review_count", ascending=False)


def build_coword_edges(tokenized: list[list[str]], minimum_edge_count: int = 3) -> pd.DataFrame:
    edges: Counter[tuple[str, str]] = Counter()
    for document in tokenized:
        terms = sorted(set(document))
        for left_index, left in enumerate(terms):
            for right in terms[left_index + 1 :]:
                edges[(left, right)] += 1
    rows = [
        {"source_term": left, "target_term": right, "document_cooccurrence": count}
        for (left, right), count in edges.items()
        if count >= minimum_edge_count
    ]
    return pd.DataFrame(rows).sort_values("document_cooccurrence", ascending=False)


def run_text_embedding_clusters(
    reviews: pd.DataFrame, config: AnalysisConfig
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Cluster compact character-ngram SVD embeddings as a reproducible semantic proxy."""
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=2, max_features=5000)
    matrix = vectorizer.fit_transform(reviews["review_text_zh"])
    dimensions = min(50, matrix.shape[0] - 1, matrix.shape[1] - 1)
    embeddings = Normalizer(copy=False).fit_transform(
        TruncatedSVD(n_components=dimensions, random_state=config.random_seed).fit_transform(matrix)
    )
    rows = []
    models = {}
    for k in range(2, 9):
        model = KMeans(n_clusters=k, n_init=30, random_state=config.random_seed).fit(embeddings)
        models[k] = model
        counts = np.bincount(model.labels_)
        rows.append(
            {
                "cluster_count": k,
                "silhouette_score": float(silhouette_score(embeddings, model.labels_, metric="cosine")),
                "minimum_cluster_size": int(counts.min()),
                "sample_size_rule_passed": bool(counts.min() >= 20),
            }
        )
    evaluation = pd.DataFrame(rows)
    eligible = evaluation.loc[evaluation["sample_size_rule_passed"]]
    if eligible.empty:
        eligible = evaluation
    selected_k = int(eligible.sort_values("silhouette_score", ascending=False).iloc[0]["cluster_count"])
    assignments = reviews[["review_id", "review_text_zh"]].copy()
    assignments["embedding_cluster"] = models[selected_k].labels_ + 1
    summary = {
        "sample_size": len(reviews),
        "selected_cluster_count": selected_k,
        "embedding_method": "Chinese character 2-4 gram TF-IDF + truncated SVD (reproducible proxy)",
        "pretrained_semantic_model_used": False,
        "limitation": "This is a lightweight lexical embedding baseline, not a pretrained language model.",
    }
    return evaluation, assignments, summary
