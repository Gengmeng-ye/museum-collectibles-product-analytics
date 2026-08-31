from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
RAW_DIR = ROOT / "data" / "raw" / "legacy"
EXTERNAL_RAW_DIR = ROOT / "data" / "raw" / "external"
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "outputs"
DATABASE_PATH = ROOT / "data" / "analytics.duckdb"
SQL_PATH = ROOT / "sql" / "analytics.sql"


def ensure_output_directories() -> None:
    for path in (INTERIM_DIR, PROCESSED_DIR, OUTPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)
