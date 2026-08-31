# Controlled data expansion report

## Scope and sources

- Products: 150 listings parsed from saved pages 1–5 of the public Hooos museum blind-box tag.
  Every row retains its listing URL, source page/position, and snapshot date (2026-08-29).
- Reviews: a fixed, length-stratified sample of 500 unique Chinese reviews drawn from 8,107
  unique texts in the CC BY 4.0 Figshare dataset `10.6084/m9.figshare.30671120.v1`.
- Evaluation: 180 sampled reviews. Aspect labels are majority votes from three published human
  coders, mapped to the project taxonomy. Sentiment labels were independently reviewed by the
  project owner; the former silver labels remain available only for audit comparison.

The pipeline uses only saved snapshots and is reproducible without live scraping.

## Main rerun results

- Product segmentation: K=5 has the best silhouette × bootstrap stability selection score.
  Cluster sizes are 26, 62, 20, 18, and 24; all exceed the minimum exploratory size of five.
- LDA: two topics remain preferred across the configured K=2–6 comparison. The result is more
  stable than the legacy six-topic claim but still broad and exploratory.
- Lightweight text embeddings: the character-ngram TF-IDF/SVD comparison selects eight clusters,
  but its best silhouette is only about 0.11. This indicates weak natural separation in short
  reviews and should be presented as a diagnostic contrast, not a superior model.
- SnowNLP: 72.8% positive, 18.8% negative, and 8.4% neutral/mixed on the expanded sample.
  Against the 180-review human audit, accuracy is 0.739 and Macro F1 is 0.459. The baseline
  particularly collapses ambiguous reviews into Positive, so the sentiment proportion is not a
  validated measure of customer satisfaction.
- Rule-based aspect extraction performs unevenly against human-coded aspects. Packaging and
  Logistics are strong; Blind-box Outcome and Price & Value need better recall/precision rules.

## Data-quality decisions

- 72/150 product pages do not display sales. Missing values remain missing and a coverage flag is
  included in segmentation.
- Product prices are displayed listing prices and may reflect promotions or starting SKUs.
- The public review workbook omits product IDs and dates. No product-review join is fabricated.
- Masked usernames are not included in processed public tables.
- Clusters describe product patterns; they do not identify authentic or counterfeit products.
