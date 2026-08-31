# Methodology

## Analytical design

The project uses two disconnected expanded datasets: public product listings and pooled reviews.
Because no product identifier was retained in the review data, product-level attributes are
never joined to review sentiment or topics. The two modules support separate findings.

## Product cleaning

- Remove fully empty columns.
- Normalize product and seller text without translating it.
- Preserve missing displayed sales as missing; never impute them as zero.
- Remove exact duplicate rows while retaining records with the same title but different seller
  or price.
- Derive transparent, rule-based museum, category, claimed-official, and price-tier fields.

`official_store_claimed` means that seller text contains a flagship/official signal. It is not
proof of authorization or authenticity.

## Statistical analysis

- Spearman correlation measures the monotonic association between price and displayed sales
  lower bounds.
- Mann-Whitney U compares distributions between claimed-official and other sellers.
- An exploratory HC3-robust OLS models `log1p(sales_lower_bound)` with `log1p(price)` and
  claimed-official status. It is associational, not causal, and excludes detailed category
  controls to avoid an excessive parameter-to-observation ratio.
- Effect sizes and confidence intervals are reported alongside p-values.

## Product segmentation

K-Means uses standardized/imputed numeric features (`log1p(price)`, displayed sales and title
length), one-hot encoded claimed-official, museum/IP, category and format fields, plus transparent
keyword flags. Candidate K=2–6 values are compared using silhouette score.
Bootstrap subsampling estimates stability through adjusted Rand index on overlapping records.
Clusters receive descriptive, data-generated profiles; they are not labeled as authentic or
counterfeit.

## Chinese NLP

Each review is one document. Jieba tokenization, a versioned stopword file, and fixed random
seeds are used. LDA candidate topic counts are compared using held-out perplexity, UMass
coherence, topic-word diversity, and top-word separation. Topics are named with their top terms instead of manually
invented business labels.

Character 2–4 gram TF-IDF reduced with truncated SVD provides a small, reproducible embedding
baseline. It is explicitly not presented as a pretrained semantic language model.

SnowNLP provides a reproducible sentiment baseline. A 180-review evaluation table is created.
Aspect labels use majority agreement from three published human coders and are mapped into the
project taxonomy. Sentiment labels were independently reviewed by the project owner using
Positive, Neutral, Negative, and Mixed. Neutral and Mixed are pooled only for the three-class
SnowNLP evaluation; the original four-class labels are retained. Silver labels remain in the
evaluation table for audit comparison and are never treated as ground truth.

The manual coding construct excludes ordinary blind-box draw disappointment: not receiving a
preferred design is treated as outcome uncertainty rather than product/service dissatisfaction.
Reviews containing only style preference or draw uncertainty are Neutral. Other statements about
quality, value, packaging, logistics, promotion, or service remain eligible sentiment evidence.

## Privacy and leakage controls

- No cookie, API key, account identifier, student identifier, or author metadata is imported.
- Masked usernames from the public source are excluded from processed public tables.
- Model selection uses training data, while LDA perplexity uses a held-out split.
- No product outcome is predicted from review features because the datasets cannot be joined.
