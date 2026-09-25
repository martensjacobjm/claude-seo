# Synthetic Bing AI Performance exports

These CSV files are **synthetic examples** for tests and documentation. Bing does
not document the column names of its AI Performance exports, so the headers here
are plausible variants that `scripts/bing_webmaster.py ai-performance` must match
tolerantly. The numbers are invented and say nothing about any real site.

Usage:

    python scripts/bing_webmaster.py ai-performance example.com \
      --file tests/fixtures/bing-ai-performance/trend.csv \
      --file tests/fixtures/bing-ai-performance/pages.csv \
      --file tests/fixtures/bing-ai-performance/queries.csv --json
