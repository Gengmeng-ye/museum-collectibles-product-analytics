from src.config import load_config
from src.external_data import (
    fixed_review_sample,
    read_figshare_reviews,
    read_hooos_product_snapshots,
)
from src.paths import EXTERNAL_RAW_DIR


def test_controlled_product_expansion_has_expected_size_and_provenance() -> None:
    products = read_hooos_product_snapshots(EXTERNAL_RAW_DIR / "hooos_museum_blind_box")
    assert len(products) == 150
    assert products["product_id"].is_unique
    assert products["source_url"].str.startswith("https://tao.hooos.com/goods_").all()


def test_controlled_review_sample_is_reproducible() -> None:
    reviews = read_figshare_reviews(
        EXTERNAL_RAW_DIR / "figshare_30671120" / "Summary of Taobao 8624 Reviews.xlsx"
    )
    config = load_config()
    first = fixed_review_sample(reviews, 500, config.random_seed)
    second = fixed_review_sample(reviews, 500, config.random_seed)
    assert len(first) == 500
    assert first["review_id"].tolist() == second["review_id"].tolist()
