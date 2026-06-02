"""Unit tests for tika-similarity.

Tests added for:
- killserver() robustness logic from PR #107 (in the 3 distance scripts)
- sunburst-cluster.py (from PR #110)

Run with: python -m unittest discover -s tests -v
Or: python -m unittest tests.test_killserver tests.test_sunburst_cluster -v
"""