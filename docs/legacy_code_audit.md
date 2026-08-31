# Legacy code and logic audit

The 2024 Word appendix and two Python files were reviewed as source material. This project
does not copy their code verbatim because the crawler contains a hard-coded Taobao session
cookie and the report contains personal identifiers.

## Reusable logic retained

- Taobao listing fields: product title, displayed price, seller, and displayed sales.
- Chinese tokenization with Jieba.
- Word-frequency and TF-IDF-style exploratory analysis.
- K-Means product segmentation and cluster-count diagnostics.
- LDA topic modeling with topic-count comparison.
- PyLDAvis-ready topic-word and document-topic outputs.
- SnowNLP sentiment scoring.
- Co-word relationships.

## Legacy code not retained verbatim

- The crawler embeds a complete session cookie and uses broad exception handling.
- Parsing relies on regular expressions and `eval`, and does not persist provenance.
- The perplexity function is commented out but later called.
- The LDA script references a missing Windows file path and undefined variables.
- The coherence script treats each token row as a separate document, producing nearly identical
  coherence values across topic counts.
- K-Means source code and verified authenticity labels are absent.
- The sentiment classification thresholds used for the legacy pie chart are absent.
- Notebook-only installation commands and local font paths are not portable.

## Replacement design

The new implementation uses immutable raw inputs, validated schemas, deterministic IDs, fixed
random seeds, held-out LDA evaluation, K-Means stability checks, documented sentiment thresholds,
DuckDB views, and automated tests. No credential-bearing extraction code is included.

