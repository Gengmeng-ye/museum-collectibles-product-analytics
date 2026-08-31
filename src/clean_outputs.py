from pathlib import Path

from src.paths import DATABASE_PATH, INTERIM_DIR, OUTPUT_DIR, PROCESSED_DIR


def _remove_generated_files(directory: Path) -> None:
    for path in directory.iterdir():
        if path.name != ".gitkeep" and path.is_file():
            path.unlink()


if __name__ == "__main__":
    for generated_dir in (INTERIM_DIR, PROCESSED_DIR, OUTPUT_DIR):
        _remove_generated_files(generated_dir)
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

