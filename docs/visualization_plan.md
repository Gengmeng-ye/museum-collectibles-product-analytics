# Visualization status and future options

Seven reproducible English static figures are implemented under `reports/figures/` and generated
with `make figures`. They cover price/tiers, assortment mix, K-Means selection, segment profiles,
LDA selection, sentiment diagnostics, and aspect-model evaluation.

## Current storytelling sequence

1. The assortment is concentrated below CNY 100.
2. Figurines and excavation kits represent distinct product-use cases.
3. K=5 is the strongest exploratory segmentation candidate.
4. Product segments differ in price, seller signal, museum/IP coverage, and sales visibility.
5. Two LDA topics are more defensible than fragmented higher-topic solutions.
6. SnowNLP over-predicts positive sentiment and is not a satisfaction KPI.
7. Transparent aspect rules work only for selected explicit categories.

## Optional future dashboard

A dashboard is optional. If added later, it should use the generated
CSV outputs and expose only useful filters: product category, product format, museum/IP, segment,
and review aspect. It must display the 78/150 sales-coverage warning and keep silver sentiment
labels visually distinct from human-coded aspects.

Do not add live scraping, authentication, cloud infrastructure, or real-time scheduling unless a
new business requirement justifies them.
