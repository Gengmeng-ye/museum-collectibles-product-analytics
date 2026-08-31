# Legacy result comparison

The generated comparison table is `outputs/legacy_comparison.csv`. It distinguishes direct
reproduction from re-estimation and rejection.

The project intentionally rejects two legacy interpretations:

1. K-Means clusters cannot prove that products are authentic or counterfeit without verified
   labels.
2. Revenue cannot be reconstructed by multiplying prices by displayed values such as `1,000+`.

The six-topic and sentiment-share findings are re-estimated because the original model input,
thresholds, and intermediate outputs were not retained.

