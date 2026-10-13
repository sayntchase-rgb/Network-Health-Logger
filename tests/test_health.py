import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from chase_core.networking.health import (
    PingResult,
    _parse_latency_ms,
    _ping_command,
    append_log,
    classify_latency,
    format_health_line,
    ping_host,
)


class NetworkHealthTests(unittest.TestCase):
    def test_classify_latency_default_threshold(self):
        self.assertEqual(classify_latency(15), "HEALTHY")
        self.assertEqual(classify_latency(100), "HEALTHY")
        self.assertEqual(classify_latency(101), "DEGRADED")
        self.assertEqual(classify_latency(None), "DEGRADED")

    def test_classify_latency_custom_threshold(self):
        self.assertEqual(classify_latency(50, healthy_max_ms=50), "HEALTHY")
        self.assertEqual(classify_latency(51, healthy_max_ms=50), "DEGRADED")

    def test_parse_latency_windows_and_linux_formats(self):
        self.assertEqual(_parse_latency_ms("Reply: time=15ms TTL=117"), 15)
        self.assertEqual(_parse_latency_ms("64 bytes: time=12.6 ms"), 13)
        self.assertEqual(_parse_latency_ms("Reply: time<1ms TTL=117"), 1)
        self.assertIsNone(_parse_latency_ms("latency unavailable"))

    @patch("chase_core.networking.health.platform.system", return_value="Windows")
    def test_ping_command_windows(self, _mock_system):
        self.assertEqual(
            _ping_command("8.8.8.8", 1000),
            ["ping", "-n", "1", "-w", "1000", "8.8.8.8"],
        )

    def test_format_health_states(self):
        timestamp = "2026-10-09 21:00:00"
        target = "8.8.8.8"

        self.assertEqual(
            format_health_line(timestamp, target, PingResult(False, None)),
            "2026-10-09 21:00:00 | 8.8.8.8 | DOWN",
        )
        self.assertEqual(
            format_health_line(timestamp, target, PingResult(True, None)),
            "2026-10-09 21:00:00 | 8.8.8.8 | latency unavailable | DEGRADED",
        )
        self.assertEqual(
            format_health_line(timestamp, target, PingResult(True, 15)),
            "2026-10-09 21:00:00 | 8.8.8.8 | 15 ms | HEALTHY",
        )
        self.assertEqual(
            format_health_line(timestamp, target, PingResult(True, 150)),
            "2026-10-09 21:00:00 | 8.8.8.8 | 150 ms | DEGRADED",
        )

    @patch("chase_core.networking.health.subprocess.run")
    def test_ping_host_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=["ping"], returncode=0, stdout="Reply: time=17ms TTL=117", stderr=""
        )
        self.assertEqual(ping_host("8.8.8.8"), PingResult(True, 17))

    @patch("chase_core.networking.health.subprocess.run", side_effect=FileNotFoundError)
    def test_ping_host_missing_executable_fails_cleanly(self, _mock_run):
        self.assertEqual(ping_host("8.8.8.8"), PingResult(False, None))

    def test_append_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "health.log"
            append_log("first", log_path)
            append_log("second", log_path)
            self.assertEqual(log_path.read_text(encoding="utf-8"), "first\nsecond\n")


if __name__ == "__main__":
    unittest.main()
