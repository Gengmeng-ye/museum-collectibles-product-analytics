# Local runbook

## First-time setup

```bash
make setup
```

## Full rebuild

```bash
make clean
make pipeline
make figures
make test
make lint
```

The rebuild reads immutable legacy files plus the saved public HTML/XLSX snapshots under
`data/raw/external/`; it makes no network request. Generated files are written
to `data/interim/`, `data/processed/`, `data/analytics.duckdb`, and `outputs/`.

`make figures` reads generated output tables and writes seven PNGs to `reports/figures/`.
`make annotate` creates the private sentiment-review template only when it does not already exist.

## Useful SQL checks

```bash
UV_CACHE_DIR=.uv-cache uv run python -c "import duckdb; print(duckdb.connect('data/analytics.duckdb').execute('SELECT * FROM category_summary').df())"
```

## Failure behavior

The pipeline stops when required columns are absent, prices are non-positive, deterministic IDs
are duplicated, or review text is empty. Missing sales are permitted and explicitly tracked.
