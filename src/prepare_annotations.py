from pathlib import Path

import pandas as pd

from src.paths import PROCESSED_DIR, ROOT

ANNOTATION_DIR = ROOT / "data" / "annotations"
ANNOTATION_PATH = ANNOTATION_DIR / "sentiment_annotation_template.csv"


def prepare_annotation_template(output_path: Path = ANNOTATION_PATH) -> Path:
    """Create a reviewer worksheet once; never overwrite completed human work."""
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing annotation file: {output_path}")
    source = pd.read_csv(PROCESSED_DIR / "review_evaluation_set.csv")
    template = source[["review_id", "review_text_zh", "manual_aspects"]].copy()
    template["manual_sentiment"] = ""
    template["reviewer_id"] = ""
    template["reviewed_at"] = ""
    template["review_notes"] = ""
    template["is_adjudicated"] = False
    template["allowed_labels"] = "Positive | Neutral | Negative | Mixed"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


if __name__ == "__main__":
    path = prepare_annotation_template()
    print(f"Created annotation template: {path}")
