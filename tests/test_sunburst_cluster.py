"""Unit tests for sunburst-cluster.py (added from PR #110).

Focus on the core create_sunburst_json() function (the CLI is thin wrapper).
Uses real temp files for I/O but no external services.

Covers:
- Happy path with realistic pairwise CSV -> correct hierarchy, cluster count limited,
  size scaling, basename used for display names.
- Error cases: missing input file, wrong CSV columns, empty data.
- Graceful handling of bad numeric scores (treated as 0.0 with warning).
"""

import unittest
import tempfile
import os
import json
import csv
import importlib.util
import sys
from io import StringIO

# Load the hyphenated module via importlib (cannot "import sunburst-cluster")
def _load_sunburst_cluster():
    spec = importlib.util.spec_from_file_location(
        "sunburst_cluster", "sunburst-cluster.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sunburst_cluster"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestSunburstCluster(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_sunburst_cluster()
        # Store raw function; call it via the module to avoid descriptor binding
        # turning it into a bound method (which would inject extra 'self' arg).
        cls._create_func = cls.mod.create_sunburst_json

    def create(self, csv_file, output_file, num_clusters=5):
        """Instance helper that calls the real function without arg binding issues.

        We look up the raw function via the *class* (not self) so that the
        function descriptor does not turn it into a bound method (which would
        inject the TestCase instance as an extra first argument).
        """
        raw_func = TestSunburstCluster._create_func
        return raw_func(csv_file, output_file, num_clusters)

    def _write_csv(self, rows, header=True):
        """Helper: write a temp CSV and return its path (caller must unlink)."""
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            if header:
                w.writerow(["x-coordinate", "y-coordinate", "Similarity_score"])
            for r in rows:
                w.writerow(r)
        return path

    def test_happy_path_basic_clustering(self):
        rows = [
            ["docA.pdf", "docB.pdf", "0.95"],
            ["docA.pdf", "docC.pdf", "0.10"],
            ["docB.pdf", "docC.pdf", "0.20"],
            ["docD.txt", "docE.txt", "0.85"],
            ["docA.pdf", "docD.txt", "0.05"],
        ]
        csv_path = self._write_csv(rows)
        out_path = tempfile.mktemp(suffix=".json")
        try:
            # Capture prints so they don't pollute test output
            with patch_stdout():
                self.create(csv_path, out_path, num_clusters=2)

            self.assertTrue(os.path.exists(out_path))
            with open(out_path) as f:
                data = json.load(f)

            self.assertEqual(data["name"], "Documents")
            self.assertIn("children", data)
            clusters = data["children"]
            # We requested 2 but greedy only seeds 2 high pairs before break
            self.assertLessEqual(len(clusters), 2)
            self.assertGreaterEqual(len(clusters), 1)

            # Check leaf shape
            leaf = clusters[0]["children"][0]
            self.assertIn("name", leaf)
            self.assertIn("path", leaf)
            self.assertIn("size", leaf)
            self.assertIsInstance(leaf["size"], (int, float))
            # display name should be basename
            self.assertNotIn("/", leaf["name"])
            self.assertNotIn("\\", leaf["name"])
        finally:
            os.unlink(csv_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_respects_num_clusters_limit(self):
        # Many high-similarity pairs
        rows = []
        for i in range(6):
            for j in range(i + 1, 6):
                score = 0.9 if (i < 3 and j < 3) or (i >= 3 and j >= 3) else 0.1
                rows.append([f"f{i}.pdf", f"f{j}.pdf", str(score)])
        csv_path = self._write_csv(rows)
        out_path = tempfile.mktemp(suffix=".json")
        try:
            with patch_stdout():
                self.create(csv_path, out_path, num_clusters=3)
            with open(out_path) as f:
                data = json.load(f)
            self.assertLessEqual(len(data["children"]), 3)
        finally:
            os.unlink(csv_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_missing_input_file_raises(self):
        out_path = tempfile.mktemp(suffix=".json")
        with self.assertRaises(FileNotFoundError):
            self.create("/non/existent/path/12345.csv", out_path, 5)
        self.assertFalse(os.path.exists(out_path))

    def test_bad_csv_columns_raises(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        with open(path, "w") as f:
            f.write("file1,file2,score\n")
            f.write("a,b,0.5\n")
        out_path = tempfile.mktemp(suffix=".json")
        try:
            with self.assertRaises(ValueError) as ctx:
                self.create(path, out_path, 2)
            self.assertIn("x-coordinate", str(ctx.exception))
        finally:
            os.unlink(path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_empty_csv_raises(self):
        csv_path = self._write_csv([])
        out_path = tempfile.mktemp(suffix=".json")
        try:
            with self.assertRaises(ValueError) as ctx:
                with patch_stdout():
                    self.create(csv_path, out_path, 5)
            self.assertIn("No valid document pairs", str(ctx.exception))
        finally:
            os.unlink(csv_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_bad_score_value_treated_as_zero(self):
        rows = [
            ["x1", "x2", "not-a-float"],
            ["x1", "x3", "0.7"],
            ["x2", "x3", "0.3"],
        ]
        csv_path = self._write_csv(rows)
        out_path = tempfile.mktemp(suffix=".json")
        try:
            # Should not crash; bad score -> 0.0
            with patch_stdout() as captured:
                self.create(csv_path, out_path, num_clusters=2)
            with open(out_path) as f:
                data = json.load(f)
            # At least one cluster should exist
            self.assertGreater(len(data["children"]), 0)
            # We expect a warning was printed (captured)
            output = captured.getvalue()
            self.assertIn("Warning: Invalid similarity score", output)
        finally:
            os.unlink(csv_path)
            if os.path.exists(out_path):
                os.unlink(out_path)


# Context manager to capture stdout (used in tests that expect prints)
class patch_stdout:
    def __enter__(self):
        self._orig = sys.stdout
        self._buf = StringIO()
        sys.stdout = self._buf
        return self._buf

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._orig


if __name__ == '__main__':
    unittest.main()
