# Resume and interview material

## Project title

**Museum Blind Box Product Analytics & Chinese NLP Evaluation**

## Resume bullets

- Rebuilt an inconsistent undergraduate market study into a reproducible Python/SQL/DuckDB
  pipeline covering 150 museum blind-box listings and 500 Chinese customer reviews, with automated
  data-quality and integrity tests.
- Developed five stable exploratory product segments using mixed numeric/categorical K-Means
  features, silhouette diagnostics, and bootstrap adjusted Rand stability; translated clusters
  into assortment and pricing hypotheses without unsupported authenticity claims.
- Re-estimated Chinese review topics with document-level LDA and held-out model selection, and
  evaluated SnowNLP against a 180-review reference set, revealing only 0.34 Macro F1 and systematic
  overprediction of positive sentiment.
- Benchmarked transparent aspect rules against published human annotations, identifying strong
  Packaging/Logistics performance and failure modes in value and blind-box outcome language.

## Thirty-second interview explanation

I revisited an undergraduate museum blind-box project and found that several reported sample sizes
and modeling interpretations could not be reproduced. I preserved the original work, rebuilt the
data flow with source-backed expansion, validation, SQL tables, modular modeling, and tests, then
used the project to show why model evaluation matters. The strongest example is SnowNLP: its raw
output looked very positive, but the evaluation showed weak Macro F1 and predictable errors on
mixed Chinese e-commerce language.

## Questions to expect

- Why is K-Means exploratory rather than a validated customer segmentation?
- How did missing displayed sales affect the feature pipeline?
- Why not translate Chinese reviews before modeling?
- Why was LDA=2 selected, and why is that not necessarily the final business taxonomy?
- What is the difference between the human-coded aspect labels and silver sentiment labels?
- What first-party data would be needed before deploying this analysis?
