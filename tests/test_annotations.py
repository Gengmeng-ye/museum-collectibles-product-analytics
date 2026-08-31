import pandas as pd
import pytest

from src.evaluation import apply_human_sentiment_labels
from src.prepare_annotations import prepare_annotation_template


def test_annotation_template_is_non_destructive(tmp_path) -> None:
    output = tmp_path / "sentiment.csv"
    prepare_annotation_template(output)
    with pytest.raises(FileExistsError):
        prepare_annotation_template(output)


def test_human_sentiment_labels_are_validated_and_pooled(tmp_path) -> None:
    evaluation = pd.DataFrame({"review_id": ["a", "b"], "review_text_zh": ["很好", "一般"]})
    annotations = tmp_path / "labels.csv"
    pd.DataFrame(
        {"review_id": ["a", "b"], "manual_sentiment": ["Positive", "Mixed"]}
    ).to_csv(annotations, index=False)
    labeled = apply_human_sentiment_labels(evaluation, annotations)
    assert labeled["manual_sentiment"].tolist() == ["Positive", "Mixed"]
    assert labeled["reference_sentiment"].tolist() == ["Positive", "Neutral / Mixed"]
    assert labeled["silver_sentiment"].notna().all()
