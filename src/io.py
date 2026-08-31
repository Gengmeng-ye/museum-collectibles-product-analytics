from pathlib import Path

import pandas as pd

from src.paths import RAW_DIR

PRODUCT_FILE = "museum_blind_box_products_legacy.xlsx"
REVIEW_FILE = "museum_blind_box_reviews_legacy.xlsx"
LEGACY_WORD_FREQUENCY_FILE = "legacy_word_frequency.xlsx"
LEGACY_TOKEN_FILE = "legacy_tokens.xlsx"


def read_legacy_products(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    return pd.read_excel(raw_dir / PRODUCT_FILE)


def read_legacy_reviews(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    return pd.read_excel(raw_dir / REVIEW_FILE)


def read_legacy_word_frequency(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    return pd.read_excel(raw_dir / LEGACY_WORD_FREQUENCY_FILE)


def read_legacy_tokens(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    return pd.read_excel(raw_dir / LEGACY_TOKEN_FILE)

