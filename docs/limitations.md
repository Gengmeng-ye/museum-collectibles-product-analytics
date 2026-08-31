# Limitations

1. The legacy report states 50 products and 120 reviews, but retained files contain 47 and 100.
2. The expanded product sample is a five-page public tag-index snapshot, not a random market sample.
3. Only 78 of 150 expanded listings display sales. Missing sales are not zeros, and revenue cannot
   be reconstructed.
4. The licensed review file does not retain product ID or review date, despite the accompanying
   crawler supporting those fields. Product-level review comparisons are therefore impossible.
5. Seller-name rules identify claimed official status, not verified authenticity.
6. K-Means uses imputation for missing displayed sales and includes a missingness indicator;
   segments may partly reflect data availability.
7. The 180 sentiment labels were user-reviewed, but the audit is class-imbalanced (146 Positive,
   13 Neutral, 12 Negative, and 9 Mixed) and has not undergone independent second-coder review.
8. LDA topics remain exploratory because short reviews can produce unstable
   word distributions.
9. The data is observational and cross-sectional. Associations cannot establish causation.
10. Results describe two source-specific samples, not the entire Chinese museum blind-box market.
