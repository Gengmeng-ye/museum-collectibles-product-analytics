# Methods

## Product analysis

Product titles, seller text, prices, and displayed sales are cleaned without translating the
Chinese source text. Missing sales stay missing. Simple title rules create museum, category,
format, store-signal, and price-tier fields.

Spearman correlation, Mann–Whitney U, and a small robust regression are used for exploratory
associations. These tests do not establish causation.

K-Means uses standardized numeric features and encoded category fields. K=2 through K=6 are
compared using silhouette score, bootstrap stability, and minimum group size. The resulting groups
describe product patterns; they are not authenticity labels.

## Review analysis

Each Chinese review is treated as one document. Jieba tokenization uses a fixed stopword list and
random seed. LDA topic counts are compared with held-out perplexity and word-based diagnostics.

SnowNLP is used as a baseline rather than ground truth. Its predictions are compared with 180
manually reviewed labels using accuracy, Macro F1, class-level results, and error cases. Neutral
and Mixed remain separate during annotation but are combined for the three-class evaluation.

Ordinary disappointment from not drawing a preferred blind-box design is treated as outcome
uncertainty, not product dissatisfaction. A review that only expresses design preference is
Neutral. Comments about quality, value, packaging, logistics, promotion, or service still count
as sentiment evidence.

Rule-based aspect labels cover Product Design, Quality, Packaging, Price & Value, Customer
Service, Logistics, Blind-box Outcome, and Gifting & Education.

## What changed from the undergraduate project

The old crawler contained a Taobao session cookie and was not reused. Several old scripts also
depended on missing paths or variables. The rebuilt version keeps the useful ideas—K-Means, LDA,
SnowNLP, Chinese tokenization, and word analysis—but adds fixed inputs, validation, model
comparison, manual sentiment review, and reproducible outputs.

Two earlier interpretations were rejected:

1. K-Means groups cannot identify authentic and counterfeit products without verified labels.
2. Revenue cannot be calculated by multiplying price by marketplace display values such as
   `1,000+`.

## Run the project

```bash
make setup
make pipeline
make public-data
make figures
make test
```

The complete rebuild needs the local source snapshots. It does not make a live scraping request.
Generated intermediate files and private annotations remain outside GitHub.
