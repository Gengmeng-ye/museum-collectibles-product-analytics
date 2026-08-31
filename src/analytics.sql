CREATE OR REPLACE VIEW product_metrics AS
SELECT
    product_id,
    museum_name,
    product_category,
    price_tier,
    official_store_claimed,
    price_cny,
    sales_lower_bound,
    sales_observed
FROM products_clean;

CREATE OR REPLACE VIEW category_summary AS
SELECT
    product_category,
    COUNT(*) AS product_count,
    ROUND(AVG(price_cny), 2) AS average_price_cny,
    MEDIAN(price_cny) AS median_price_cny,
    COUNT(sales_lower_bound) AS listings_with_displayed_sales,
    MEDIAN(sales_lower_bound) AS median_displayed_sales_when_available
FROM products_clean
GROUP BY product_category;

CREATE OR REPLACE VIEW sentiment_summary AS
SELECT
    sentiment_label,
    COUNT(*) AS review_count,
    ROUND(AVG(sentiment_score), 4) AS average_sentiment_score
FROM reviews_scored
GROUP BY sentiment_label;
