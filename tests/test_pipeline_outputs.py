from src.paths import DATABASE_PATH, OUTPUT_DIR, PROCESSED_DIR, ROOT


def test_expected_pipeline_outputs_exist() -> None:
    expected = [
        PROCESSED_DIR / "products_clean.csv",
        PROCESSED_DIR / "reviews_clean.csv",
        PROCESSED_DIR / "products_segmented.csv",
        PROCESSED_DIR / "reviews_scored.csv",
        OUTPUT_DIR / "legacy_comparison.csv",
        OUTPUT_DIR / "model_report.json",
        DATABASE_PATH,
    ]
    assert all(path.exists() for path in expected)


def test_report_figures_exist_and_are_nonempty() -> None:
    figure_dir = ROOT / "figures"
    figures = sorted(figure_dir.glob("*.png"))
    assert len(figures) == 7
    assert all(path.stat().st_size > 20_000 for path in figures)
