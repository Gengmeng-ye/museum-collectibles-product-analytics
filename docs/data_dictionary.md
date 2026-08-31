# Data dictionary

## `products_clean`

| Field | Type / unit | Missing-value rule | Description and source |
|---|---|---|---|
| `product_id` | string | Not allowed | Deterministic SHA-256-based ID generated from source URL. |
| `source_page`, `source_position` | integer | Not allowed | Position in the saved public tag-index snapshot. |
| `product_name_zh` | Chinese text | Empty not allowed | Product title from the public listing index. |
| `seller_name_zh` | Chinese text | Empty not allowed | Displayed seller name. |
| `price_cny` | float, CNY | Invalid rows fail validation | Displayed listing price; may be an SKU-level starting price. |
| `sales_display` | string | Missing means not shown | Displayed value such as `29`; never filled with zero. |
| `sales_lower_bound` | float, units | Nullable | Numeric displayed sales count where available. |
| `sales_observed` | boolean | Not allowed | Whether the snapshot displayed a sales value. |
| `official_store_claimed` | boolean | Not allowed | Seller-text rule; not verified authorization. |
| `museum_name` | category | `Other / Unclear` | Rule-derived English museum/IP label. |
| `product_category` | category | `Other Cultural Product` | Rule-derived English product taxonomy. |
| `product_format` | category | `Other Blind-box Format` | Rule-derived format such as figurine, magnet, or excavation kit. |
| `museum_ip_flag` | boolean | Not allowed | Whether a known museum/IP rule matched. |
| `keyword_*` | boolean | Not allowed | Transparent title flags used in segmentation. |
| `price_tier` | category | Not allowed | Configured price band in CNY. |
| `title_length_chars` | integer, characters | Not allowed | Length of the Chinese product title. |
| `source_platform` | string | Not allowed | Reported platform provenance. |
| `source_scope` | string | Not allowed | Known collection scope and provenance limitation. |
| `source_url` | URL | Not allowed | Public listing-detail URL used as row-level provenance. |
| `collection_date` | ISO date | Not allowed | Snapshot collection date. |

## `reviews_clean` and `reviews_scored`

| Field | Type / unit | Missing-value rule | Description and source |
|---|---|---|---|
| `review_id` | string | Not allowed | Deterministic ID generated from review text. |
| `review_text_zh` | Chinese text | Empty not allowed | Original review; intentionally not machine-translated. |
| `review_length_chars` | integer | Must be positive | Chinese character/string length. |
| `aspects` | pipe-separated categories | Empty means no rule match | Transparent multi-label product-experience aspects. |
| `aspect_count` | integer | Not allowed | Number of detected aspects. |
| `source_dataset_doi` | DOI | Not allowed | Figshare dataset DOI. |
| `product_link_available` | boolean | Always false | The published research workbook omits product IDs. |
| `sentiment_score` | float, 0–1 | Generated only in scored table | SnowNLP sentiment score. |
| `sentiment_label` | category | Generated only in scored table | Thresholded descriptive label. |

## Modeling outputs

`products_segmented.csv` adds `cluster_id`. `review_topic_assignments.csv` adds dominant-topic
and per-topic probabilities. Topic labels are generated from top Chinese terms so that the
pipeline does not invent unsupported English interpretations.

`review_evaluation_set.csv` contains 180 reviews. `manual_aspects` comes from a majority vote of
three published human coders after a documented taxonomy mapping. `reference_sentiment` is a
rule-assisted assistant silver label and must not be described as human ground truth.
