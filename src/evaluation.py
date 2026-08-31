from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

from src.rules import normalize_text

ASPECT_MAP = {
    "造型美感": "Product Design",
    "色彩搭配": "Product Design",
    "创意表达": "Product Design",
    "制造工艺": "Quality",
    "物体材料": "Quality",
    "产品气味": "Quality",
    "包装质量": "Packaging",
    "价格": "Price & Value",
    "物流速度": "Logistics",
    "附加价值": "Gifting & Education",
    "文化叙事": "Gifting & Education",
    "文化传播": "Gifting & Education",
    "参与互动": "Blind-box Outcome",
    "系列主题": "Blind-box Outcome",
}

POSITIVE = ("喜欢", "满意", "好看", "可爱", "精致", "不错", "推荐", "惊喜", "完美", "超值", "开心", "爱死", "很好")
NEGATIVE = ("失望", "不好", "不值", "太贵", "瑕疵", "破损", "坏", "难看", "生气", "不开心", "差", "慢", "臭", "划", "少发", "漏发", "退货")


def _split_labels(value: object) -> set[str]:
    if pd.isna(value):
        return set()
    return {part.strip() for part in str(value).split(",") if part.strip()}


def _map_aspects(labels: set[str]) -> set[str]:
    return {ASPECT_MAP[label] for label in labels if label in ASPECT_MAP}


def build_human_aspect_evaluation(
    sampled_reviews: pd.DataFrame, coder_paths: list[Path], size: int, seed: int
) -> pd.DataFrame:
    coder_frames = []
    for index, path in enumerate(coder_paths, 1):
        data = pd.read_excel(path, usecols=[1, 3])
        data.columns = ["review_text_zh", f"coder_{index}"]
        data["review_text_zh"] = data["review_text_zh"].map(normalize_text)
        data = data.drop_duplicates("review_text_zh")
        coder_frames.append(data)
    merged = coder_frames[0]
    for frame in coder_frames[1:]:
        merged = merged.merge(frame, on="review_text_zh", how="inner")
    merged = sampled_reviews[["review_id", "review_text_zh"]].merge(merged, on="review_text_zh")

    def consensus(row: pd.Series) -> str:
        votes = [_map_aspects(_split_labels(row[f"coder_{i}"])) for i in range(1, 4)]
        labels = sorted({label for label in set().union(*votes) if sum(label in vote for vote in votes) >= 2})
        return "|".join(labels)

    merged["manual_aspects"] = merged.apply(consensus, axis=1)
    merged["annotation_source"] = "Majority vote of three human coders (published dataset)"
    merged["adjudication_status"] = "Human coder majority; mapping to portfolio aspect taxonomy"
    positive = merged.loc[merged["manual_aspects"].ne("")]
    negative = merged.loc[merged["manual_aspects"].eq("")]
    take_positive = min(int(size * 0.8), len(positive))
    chosen = pd.concat(
        [
            positive.sample(take_positive, random_state=seed),
            negative.sample(min(size - take_positive, len(negative)), random_state=seed),
        ]
    )
    if len(chosen) < size:
        remainder = merged.loc[~merged.index.isin(chosen.index)]
        chosen = pd.concat([chosen, remainder.sample(size - len(chosen), random_state=seed)])
    return chosen.sample(frac=1, random_state=seed).head(size).reset_index(drop=True)


def silver_sentiment_label(text: str) -> tuple[str, str]:
    positive = any(term in text for term in POSITIVE)
    negative = any(term in text for term in NEGATIVE) or bool(
        __import__("re").search(r"不.{0,2}(喜欢|满意|推荐|好看|可爱)", text)
    )
    if positive and negative:
        return "Neutral / Mixed", "mixed positive and negative cues"
    if negative:
        return "Negative", "negative cue"
    if positive:
        return "Positive", "positive cue"
    return "Neutral / Mixed", "no unambiguous sentiment cue"


def add_silver_sentiment_labels(evaluation: pd.DataFrame) -> pd.DataFrame:
    data = evaluation.copy()
    labeled = data["review_text_zh"].map(silver_sentiment_label)
    data["reference_sentiment"] = labeled.map(lambda value: value[0])
    data["sentiment_rationale"] = labeled.map(lambda value: value[1])
    data["sentiment_annotation_source"] = "Rule-assisted assistant annotation; not human ground truth"
    return data


def apply_human_sentiment_labels(evaluation: pd.DataFrame, annotation_path: Path) -> pd.DataFrame:
    """Attach locally reviewed labels while retaining the silver baseline for audit."""
    annotations = pd.read_csv(annotation_path, encoding="utf-8-sig")
    required = {"review_id", "manual_sentiment"}
    if missing := required.difference(annotations.columns):
        raise ValueError(f"Human annotation file is missing columns: {sorted(missing)}")
    allowed = {"Positive", "Neutral", "Negative", "Mixed"}
    if annotations["review_id"].duplicated().any():
        raise ValueError("Human annotation review_id values must be unique")
    if annotations["manual_sentiment"].isna().any():
        raise ValueError("Human sentiment labels must be complete")
    unexpected = set(annotations["manual_sentiment"]).difference(allowed)
    if unexpected:
        raise ValueError(f"Unexpected human sentiment labels: {sorted(unexpected)}")

    data = add_silver_sentiment_labels(evaluation)
    data = data.rename(
        columns={
            "reference_sentiment": "silver_sentiment",
            "sentiment_rationale": "silver_sentiment_rationale",
            "sentiment_annotation_source": "silver_annotation_source",
        }
    )
    fields = ["review_id", "manual_sentiment"]
    if "is_adjudicated" in annotations.columns:
        fields.append("is_adjudicated")
    data = data.merge(annotations[fields], on="review_id", how="left", validate="one_to_one")
    if data["manual_sentiment"].isna().any():
        missing_count = int(data["manual_sentiment"].isna().sum())
        raise ValueError(f"Human labels do not cover {missing_count} evaluation rows")
    data["reference_sentiment"] = data["manual_sentiment"].replace(
        {"Neutral": "Neutral / Mixed", "Mixed": "Neutral / Mixed"}
    )
    data["sentiment_rationale"] = "Independent human review; Neutral and Mixed pooled for three-class SnowNLP evaluation"
    data["sentiment_annotation_source"] = "User-reviewed human labels"
    return data


def evaluate_sentiment(scored: pd.DataFrame, reference: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    joined = reference.merge(
        scored[["review_id", "sentiment_label", "sentiment_score"]], on="review_id", how="inner"
    )
    labels = ["Negative", "Neutral / Mixed", "Positive"]
    report = classification_report(
        joined["reference_sentiment"], joined["sentiment_label"], labels=labels,
        output_dict=True, zero_division=0,
    )
    metrics = pd.DataFrame(report).T.reset_index(names="class_or_average")
    matrix = pd.DataFrame(
        confusion_matrix(joined["reference_sentiment"], joined["sentiment_label"], labels=labels),
        index=[f"actual_{label}" for label in labels], columns=[f"predicted_{label}" for label in labels],
    ).reset_index(names="actual_label")
    summary = {
        "evaluation_rows": len(joined),
        "accuracy": float(accuracy_score(joined["reference_sentiment"], joined["sentiment_label"])),
        "macro_f1": float(f1_score(joined["reference_sentiment"], joined["sentiment_label"], labels=labels, average="macro")),
        "human_ground_truth": reference.get("sentiment_annotation_source", pd.Series(dtype=str)).eq(
            "User-reviewed human labels"
        ).all(),
        "has_human_labeled_validation_set": reference.get(
            "sentiment_annotation_source", pd.Series(dtype=str)
        ).eq("User-reviewed human labels").all(),
        "accuracy_claim_supported": reference.get(
            "sentiment_annotation_source", pd.Series(dtype=str)
        ).eq("User-reviewed human labels").all(),
        "claim_constraint": (
            "Evaluation uses independent human review; Neutral and Mixed are pooled because SnowNLP produces three classes."
            if reference.get("sentiment_annotation_source", pd.Series(dtype=str)).eq("User-reviewed human labels").all()
            else "Diagnostic silver-label comparison only; a human sentiment audit is still required."
        ),
    }
    return metrics, matrix, summary


def sentiment_error_cases(scored: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    joined = reference.merge(
        scored[["review_id", "sentiment_label", "sentiment_score"]], on="review_id", how="inner"
    )
    errors = joined.loc[joined["reference_sentiment"].ne(joined["sentiment_label"])].copy()
    errors["error_type"] = (
        errors["reference_sentiment"].astype(str)
        + " predicted as "
        + errors["sentiment_label"].astype(str)
    )
    errors["distance_from_neutral"] = (errors["sentiment_score"] - 0.5).abs()
    columns = [
        "review_id",
        "review_text_zh",
        "reference_sentiment",
        "sentiment_label",
        "sentiment_score",
        "error_type",
        "sentiment_rationale",
    ]
    return errors.sort_values(
        ["error_type", "distance_from_neutral"], ascending=[True, False]
    )[columns].reset_index(drop=True)


def human_adjudication_candidates(scored: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    """Flag a compact set for second review without changing any human label."""
    if "manual_sentiment" not in reference.columns:
        return pd.DataFrame()
    joined = reference.merge(
        scored[["review_id", "sentiment_label", "sentiment_score"]], on="review_id", how="inner"
    )
    # Ordinary draw disappointment is outside the sentiment construct; only controllable
    # product/service/value language is used for label-QA flags.
    negative_pattern = (
        r"不值|不喜欢|太差|品控一般|体验一般|没有一个喜欢|破损|损坏|欺骗|"
        r"等.{0,4}太长|太贵|吃亏|黑点|底座不行|粗制乱造|客服.{0,8}(?:不|差|慢|拒)"
    )
    positive_pattern = r"喜欢|好看|可爱|精致|满意|不错|划算|很好|推荐|期待"
    has_negative = joined["review_text_zh"].str.contains(negative_pattern, regex=True)
    has_positive = joined["review_text_zh"].str.contains(positive_pattern, regex=True)
    needs_review = (
        (joined["manual_sentiment"].eq("Neutral") & has_negative)
        | (joined["manual_sentiment"].eq("Positive") & has_negative & has_positive)
        | (joined["manual_sentiment"].eq("Mixed") & ~(has_negative & has_positive))
    )
    candidates = joined.loc[needs_review].copy()
    candidates["review_reason"] = "Human label conflicts with explicit polarity or mixed-sentiment cues; second review recommended"
    columns = [
        "review_id", "review_text_zh", "manual_sentiment", "sentiment_label",
        "sentiment_score", "silver_sentiment", "review_reason",
    ]
    return candidates[columns].reset_index(drop=True)


def evaluate_rule_aspects(reviews: pd.DataFrame, reference: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    joined = reference.merge(reviews[["review_id", "aspects"]], on="review_id", how="inner")
    labels = sorted(set(ASPECT_MAP.values()))
    rows = []
    total_tp = total_fp = total_fn = 0
    for label in labels:
        actual = joined["manual_aspects"].map(
            lambda value, current_label=label: current_label in str(value).split("|")
        )
        predicted = joined["aspects"].map(
            lambda value, current_label=label: current_label in str(value).split("|")
        )
        tp = int((actual & predicted).sum())
        fp = int((~actual & predicted).sum())
        fn = int((actual & ~predicted).sum())
        total_tp += tp
        total_fp += fp
        total_fn += fn
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        rows.append(
            {
                "aspect": label,
                "support": int(actual.sum()),
                "precision": precision,
                "recall": recall,
                "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            }
        )
    micro_precision = total_tp / (total_tp + total_fp) if total_tp + total_fp else 0.0
    micro_recall = total_tp / (total_tp + total_fn) if total_tp + total_fn else 0.0
    summary = {
        "evaluation_rows": len(joined),
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": 2 * micro_precision * micro_recall / (micro_precision + micro_recall)
        if micro_precision + micro_recall
        else 0.0,
        "annotation_source": "Majority vote of three published human coders",
    }
    return pd.DataFrame(rows), summary
