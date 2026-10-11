"""Test the unchanged script without sending pings or touching real logs."""

from contextlib import redirect_stdout
from datetime import datetime
import io
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "network_health_logger.py"
FIXED_TIME = datetime(2026, 10, 7, 6, 51, 43)
PREFIX = "2026-10-07 06:51:43 | 8.8.8.8 | "


class LoggerTests(unittest.TestCase):
    def setUp(self):
        # Each test gets its own working directory and real, disposable log.
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        previous_directory = Path.cwd()
        self.addCleanup(os.chdir, previous_directory)
        os.chdir(directory.name)
        self.log = Path("network_health.log")

    def run_logger(self, stdout, returncode=0):
        """Replace ping and the clock, then execute the script as usual."""
        result = subprocess.CompletedProcess([], returncode, stdout, "")
        console = io.StringIO()
        with patch("subprocess.run", return_value=result) as ping, \
                patch("datetime.datetime") as clock, redirect_stdout(console):
            clock.now.return_value = FIXED_TIME
            runpy.run_path(str(SCRIPT), run_name="__main__")
        ping.assert_called_once_with(
            ["ping", "-n", "1", "8.8.8.8"], capture_output=True, text=True
        )
        return console.getvalue()

    def assert_result(self, reply, expected, returncode=0):
        expected_line = PREFIX + expected + "\n"
        self.assertEqual(self.run_logger(reply, returncode), expected_line)
        self.assertEqual(self.log.read_text(), expected_line)

    def test_fast_reply_is_healthy(self):
        self.assert_result("Reply: bytes=32 time=15ms TTL=115", "15 ms | HEALTHY")

    def test_exactly_100_ms_is_healthy(self):
        self.assert_result("Reply: bytes=32 time=100ms TTL=115", "100 ms | HEALTHY")

    def test_101_ms_is_degraded(self):
        self.assert_result("Reply: bytes=32 time=101ms TTL=115", "101 ms | DEGRADED")

    def test_submillisecond_reply_keeps_existing_one_ms_display(self):
        self.assert_result("Reply: bytes=32 time<1ms TTL=128", "1 ms | HEALTHY")

    def test_success_without_latency_is_degraded(self):
        self.assert_result("No recognizable timing", "latency unavailable | DEGRADED")

    def test_failed_ping_is_down(self):
        self.assert_result("Request timed out.", "DOWN", returncode=1)

    def test_failed_ping_takes_priority_over_timing_text(self):
        self.assert_result("time=15ms", "DOWN", returncode=1)

    def test_repeated_runs_append_and_preserve_existing_log(self):
        existing = "previous historical entry\n"
        self.log.write_text(existing)
        first = self.run_logger("time=15ms")
        second = self.run_logger("Request timed out.", returncode=1)
        self.assertEqual(
            self.log.read_text(),
            existing + PREFIX + "15 ms | HEALTHY\n" + PREFIX + "DOWN\n",
        )
        self.assertEqual(self.log.read_text(), existing + first + second)


if __name__ == "__main__":
    unittest.main()
