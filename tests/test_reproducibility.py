import pandas as pd

from src.config import load_config
from src.segmentation import run_product_segmentation


def test_segmentation_is_reproducible() -> None:
    products = pd.read_csv("data/processed/products_clean.csv")
    first = run_product_segmentation(products, load_config())[0]["cluster_id"]
    second = run_product_segmentation(products, load_config())[0]["cluster_id"]
    assert first.equals(second)

