from pathlib import Path

import duckdb
import pandas as pd

from src.paths import DATABASE_PATH, SQL_PATH


def build_database(
    products: pd.DataFrame,
    reviews: pd.DataFrame,
    scored_reviews: pd.DataFrame,
    database_path: Path = DATABASE_PATH,
) -> None:
    if database_path.exists():
        database_path.unlink()
    connection = duckdb.connect(str(database_path))
    try:
        connection.register("products_frame", products)
        connection.register("reviews_frame", reviews)
        connection.register("reviews_scored_frame", scored_reviews)
        connection.execute("CREATE TABLE products_clean AS SELECT * FROM products_frame")
        connection.execute("CREATE TABLE reviews_clean AS SELECT * FROM reviews_frame")
        connection.execute("CREATE TABLE reviews_scored AS SELECT * FROM reviews_scored_frame")
        connection.execute(SQL_PATH.read_text(encoding="utf-8"))
    finally:
        connection.close()


def export_sql_views(database_path: Path = DATABASE_PATH) -> dict[str, pd.DataFrame]:
    connection = duckdb.connect(str(database_path), read_only=True)
    try:
        return {
            "sql_product_metrics": connection.execute("SELECT * FROM product_metrics").df(),
            "sql_category_summary": connection.execute(
                "SELECT * FROM category_summary ORDER BY product_count DESC"
            ).df(),
            "sql_sentiment_summary": connection.execute(
                "SELECT * FROM sentiment_summary ORDER BY review_count DESC"
            ).df(),
        }
    finally:
        connection.close()

