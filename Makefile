.PHONY: setup pipeline annotate figures test lint clean

setup:
	UV_CACHE_DIR=.uv-cache uv sync --dev

pipeline:
	LOKY_MAX_CPU_COUNT=4 UV_CACHE_DIR=.uv-cache uv run python -m src.pipeline

annotate:
	UV_CACHE_DIR=.uv-cache uv run python -m src.prepare_annotations

figures:
	XDG_CACHE_HOME=.cache MPLCONFIGDIR=.mpl-cache UV_CACHE_DIR=.uv-cache uv run python -m src.visualization

test:
	LOKY_MAX_CPU_COUNT=4 UV_CACHE_DIR=.uv-cache uv run pytest -q

lint:
	UV_CACHE_DIR=.uv-cache uv run ruff check src tests

clean:
	UV_CACHE_DIR=.uv-cache uv run python -m src.clean_outputs
