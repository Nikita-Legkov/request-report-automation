import tempfile
import unittest
from datetime import date
from pathlib import Path

from report import build_metrics, generate, load_rows


class ReportTest(unittest.TestCase):
    def test_demo_metrics_and_files(self):
        source = Path(__file__).parent / "data" / "demo_requests.csv"
        rows = load_rows(source)
        metrics = build_metrics(rows, date(2026, 8, 9))
        self.assertEqual(8, metrics["total"])
        self.assertEqual(3, metrics["overdue"])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            generate(source, output, date(2026, 8, 9))
            self.assertTrue((output / "report.html").exists())
            self.assertTrue((output / "summary.csv").exists())


if __name__ == "__main__":
    unittest.main()
