# Museum Collectibles: Product Analytics & Chinese NLP

An undergraduate web-scraping study rebuilt as a reproducible product analytics portfolio project.
The project combines a market map of museum collectibles with an independent audit of Chinese
review-analysis methods. It keeps the useful technical ideas from the original work, corrects the
parts that could not be verified, and translates the results into decisions a product team could
understand and test.

> **Portfolio positioning:** Product Analytics + applied Data Science, with a lightweight
> Python/SQL/DuckDB data pipeline. Models use original Chinese text; documentation and
> recruiter-facing outputs are in English.

## Project background

The original undergraduate project examined museum-themed blind boxes sold on Taobao. Product
information and customer reviews were collected through web scraping and then analyzed with
Excel/SPSS-style outputs, K-Means clustering, LDA topic modeling, and SnowNLP sentiment scores.
That work established the core question—how cultural products are positioned and discussed—but
the retained files were incomplete: only 47 product records and 100 reviews remained, while the
report referred to 50 products and 120 reviews. Some results existed only as screenshots or copied
outputs, and several interpretations could not be reproduced from the surviving data.

This repository treats that mismatch as a data-audit problem rather than hiding it. The original
materials are preserved unchanged, and the analysis is rebuilt around two clearly separated
datasets:

1. **Product Landscape:** 150 public Taobao/Tmall listing snapshots are used to describe price
   structure, product formats, official-store signals, and exploratory product positioning.
2. **Customer Voice Lab:** a fixed sample of 500 Chinese reviews, drawn from 8,107 unique published
   review texts, is used to test topic, aspect, and sentiment methods. A 180-review human audit set
   evaluates SnowNLP instead of treating its output as ground truth.

The two datasets do not contain a defensible product-level key, so they are not joined. Together
they answer two complementary questions: **what the market offers**, and **what automated review
analysis can reliably tell a product team**.

## Business questions

- How is the public museum-collectibles assortment structured by price, format, and store type?
- Which patterns form useful exploratory product groups?
- What do Chinese reviews discuss, and how reliably can automated methods identify those signals?
- Which findings can support a product decision, and which remain outside the available evidence?

## Key findings

- **137 of 150 indexed products are priced at or below CNY 100.** The median displayed price is
  CNY 59, suggesting a mass-market/gifting assortment rather than a premium-only market.
- **K=5 is the strongest exploratory segmentation solution** across silhouette and bootstrap
  stability. Segments distinguish museum excavation kits, broad collectible assortments, budget
  marketplace kits, premium museum figurines, and listings with stronger sales visibility.
- **Two broad LDA topics are more defensible than the legacy six-topic claim.** Increasing the
  topic count sharply worsens held-out perplexity and reduces topic diversity.
- **SnowNLP is not a reliable satisfaction metric here.** It predicts 72.8% of reviews as
  positive, but achieves 0.739 accuracy and only 0.459 Macro F1 against 180 user-reviewed labels.
  Positive performance is much stronger than performance on minority classes.
- **Aspect rules are uneven.** Packaging and Logistics align well with published human coding;
  Blind-box Outcome and Price & Value require stronger language coverage.

![Price distribution](reports/figures/01-price-and-tier-distribution.png)

![Product segment profiles](reports/figures/04-segment-profile-heatmap.png)

An interactive recruiter-facing dashboard is available under [`dashboard/`](dashboard/README.md)
with separate Product Landscape and Customer Voice Lab pages.

## Data

| Dataset | Portfolio scope | Provenance |
|---|---:|---|
| Product listings | 150 | Public Hooos Taobao/Tmall index snapshots, pages 1–5, collected 2026-08-29 |
| Review analysis sample | 500 | Fixed length-stratified sample from 8,107 unique Figshare review texts |
| Aspect evaluation | 180 | Majority vote of three published human coders, mapped to this project taxonomy |
| Sentiment evaluation | 180 | User-reviewed Positive/Neutral/Negative/Mixed labels; local/private audit file |

The review source is the CC BY 4.0 Figshare dataset accompanying Huang (2026), *“Opening the Box
to Explore the Contents”*. The published review workbook does not retain product IDs or review
dates, so product-review joins are not fabricated. Only 78/150 product listings display sales;
missing sales remain missing rather than being converted to zero.

## Reproducible workflow

```text
Saved raw snapshots
        ↓
Source-specific parsing and cleaning
        ↓
Data validation and deterministic IDs
        ↓
Analysis-ready CSV tables + DuckDB views
        ↓
Statistical analysis, K-Means, LDA, text clusters, SnowNLP
        ↓
Model diagnostics, error cases, and visualization-ready outputs
```

Core methods:

- Python modules for parsing, cleaning, validation, modeling, and evaluation;
- SQL analytical views in DuckDB;
- HC3-robust exploratory regression and non-parametric tests;
- mixed numeric/categorical K-Means features, K=2–6 comparison, bootstrap ARI stability;
- Chinese Jieba tokenization and LDA evaluated with held-out perplexity, UMass coherence,
  diversity, and separation;
- character n-gram TF-IDF + SVD clustering as a lightweight text-representation comparison;
- SnowNLP and rule-based aspect extraction with confusion matrices and error analysis.

## Run locally

Python 3.11–3.13 and [uv](https://docs.astral.sh/uv/) are recommended.

```bash
make setup
make pipeline
make figures
make test
make lint
```

To create the non-destructive human sentiment review worksheet once:

```bash
make annotate
```

The annotation command refuses to overwrite an existing worksheet.

## Project structure

```text
config/                 Versioned analysis settings and Chinese stopwords
data/raw/               Immutable legacy and external-source snapshots
data/processed/         Generated analysis-ready tables
data/annotations/       Human-review worksheet (never overwritten)
docs/                   Methodology, limitations, dictionary, and audit trail
reports/figures/        Reproducible English static figures
sql/                    DuckDB analytical views
src/                    Modular Python pipeline and visualization code
tests/                  Data quality, integrity, and reproducibility tests
outputs/                Generated model diagnostics and reporting tables
```

## What changed from the undergraduate project?

- Corrected the retained sample discrepancy (47 products/100 reviews versus 50/120 reported).
- Rejected the unsupported interpretation of K-Means clusters as authentic/counterfeit products.
- Fixed the legacy LDA document-definition and model-selection problems.
- Evaluated SnowNLP instead of treating its scores as true labels.
- Replaced manual result transcription with code-generated tables, tests, and documented limits.

See [the analysis report](reports/analysis_report.md), [methodology](docs/methodology.md),
[data dictionary](docs/data_dictionary.md), and [limitations](docs/limitations.md).

## Limitations

This is an exploratory, source-specific observational study—not a market census or causal study.
Displayed prices may be promotional/SKU-starting prices, sales coverage is incomplete, seller-name
signals do not verify authorization, and reviews cannot be linked to individual products. The
human sentiment audit is class-imbalanced and should not be treated as a population satisfaction
estimate.

Code is licensed under MIT. Third-party datasets and snapshots retain their original terms; see
`THIRD_PARTY_DATA.md` before redistribution.
