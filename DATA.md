# Data

This project uses separate product and review datasets. They do not share a usable product ID and
are never joined together.

## Where the data came from

The retained undergraduate files contain 47 Taobao product rows and 100 reviews. The written
report referred to 50 products and 120 reviews, so these files are used only to check the earlier
work.

The current product analysis uses 150 listings collected on 2026-08-29 from five saved pages of
the public Hooos Taobao/Tmall museum blind-box index. This is a new convenience sample, not an
extension of the original 47 rows.

The text analysis uses 500 reviews sampled from 8,107 unique Chinese review texts in Xuanrui
Huang's Figshare dataset, “Opening the Box to Explore the Contents” All raw data
([DOI](https://doi.org/10.6084/m9.figshare.30671120.v1), CC BY 4.0). A subset of 180 reviews was
manually checked for sentiment evaluation.

Raw snapshots, seller names, listing links, complete review text, and private annotation notes are
not published. The anonymized files available on GitHub are:

| File | Rows | Contents |
|---|---:|---|
| [`data/products.csv`](data/products.csv) | 150 | Price, format, store signals, sales coverage, and cluster |
| [`data/reviews.csv`](data/reviews.csv) | 500 | Topic, aspect, and sentiment model outputs |
| [`data/sentiment_evaluation.csv`](data/sentiment_evaluation.csv) | 180 | Human labels compared with SnowNLP |
| [`data/summaries/`](data/summaries/) | varies | Small summary tables used in the analysis |

## Important fields

### Products

| Field | Meaning |
|---|---|
| `product_id` | An anonymized, deterministic row ID |
| `price_cny` | Displayed listing price in Chinese yuan |
| `sales_lower_bound` | Numeric displayed sales where available |
| `sales_observed` | Whether a sales figure appeared on the page |
| `official_store_claimed` | Seller wording suggests an official/flagship store; not verified authorization |
| `museum_name` | Museum or IP category derived from title rules |
| `product_category` | Broad product category |
| `product_format` | Figurine, excavation kit, magnet, plush/charm, gift set, or other |
| `price_tier` | Configured price band |
| `cluster_id` | Exploratory K-Means group |

### Reviews

| Field | Meaning |
|---|---|
| `review_id` | An anonymized, deterministic row ID |
| `review_length_chars` | Length of the original Chinese review |
| `aspects` | Rule-based multi-label aspects |
| `sentiment_score` | SnowNLP score from 0 to 1 |
| `sentiment_label` | SnowNLP label after applying fixed thresholds |
| `dominant_topic_id` | Most likely LDA topic |
| `manual_sentiment` | Manually reviewed sentiment label in the evaluation file |

## Limits

- The 150 listings are not a random sample of the full market.
- Only 78 listings display sales. Missing sales are not changed to zero.
- Displayed prices may be promotional or starting-SKU prices.
- Seller wording cannot prove authenticity or authorization.
- The review source has no usable product ID or date.
- The 180-review sentiment set is class-imbalanced and was not independently double-coded.
- The data cannot support market-share, revenue, demand, or causal claims.

The repository's MIT license covers original code and documentation only. Figshare data remains
under CC BY 4.0. Hooos page content is not covered by the MIT license.
