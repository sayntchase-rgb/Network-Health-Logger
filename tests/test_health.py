import tempfile
import unittest
from pathlib import Path

from chase_core.networking.health import (
    PingResult,
    append_log,
    classify_latency,
    format_health_line,
)


class NetworkHealthTests(unittest.TestCase):
    def test_classify_latency(self):
        self.assertEqual(classify_latency(15), "HEALTHY")
        self.assertEqual(classify_latency(100), "HEALTHY")
        self.assertEqual(classify_latency(101), "DEGRADED")
        self.assertEqual(classify_latency(None), "DEGRADED")

    def test_format_down(self):
        line = format_health_line(
            "2026-10-09 21:00:00",
            "8.8.8.8",
            PingResult(reachable=False, latency_ms=None),
        )
        self.assertEqual(line, "2026-10-09 21:00:00 | 8.8.8.8 | DOWN")

    def test_append_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "health.log"
            append_log("first", log_path)
            append_log("second", log_path)
            self.assertEqual(log_path.read_text(encoding="utf-8"), "first\nsecond\n")


if __name__ == "__main__":
    unittest.main()
