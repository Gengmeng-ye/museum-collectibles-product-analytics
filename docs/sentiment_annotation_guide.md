# Human sentiment annotation guide

Use `data/annotations/sentiment_annotation_template.csv`. Read the original Chinese text and
enter exactly one label in `manual_sentiment`.

- `Positive`: clearly favorable overall experience or recommendation.
- `Neutral`: factual content without a clear favorable or unfavorable stance.
- `Negative`: clearly unfavorable experience, complaint, rejection, or disappointment.
- `Mixed`: meaningful positive and negative opinions appear in the same review.

Do not infer sentiment from SnowNLP, product price, aspect labels, or punctuation alone. Preserve
negation (for example, “not worth it”), distinguish a complaint from quoted seller language, and
use `Mixed` when a defect is described alongside clear satisfaction. Record uncertainty or slang
in `review_notes`. Set `is_adjudicated=True` only after a second review of uncertain cases.

### Blind-box outcome rule

Random draw outcomes are excluded from the product/service sentiment construct. A reviewer merely
not receiving a preferred or hidden design is not treated as product dissatisfaction. If the text
contains only draw-result or design-preference uncertainty, label it `Neutral`. When the same
review evaluates quality, value, packaging, logistics, service, or another controllable experience,
assign sentiment using only those evaluative statements. Explicit complaints about manipulated
odds, misleading promotion, duplicate fulfillment, or service handling remain eligible evidence
because they concern the purchase experience rather than ordinary blind-box randomness.

The pipeline uses the completed local human-review file when available and otherwise falls back to
assistant-generated silver labels. Neutral and Mixed remain separate in the annotation source but
are pooled for three-class SnowNLP evaluation. The private annotation file is ignored by Git.
