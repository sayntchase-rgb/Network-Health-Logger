import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from chase_core.networking.health import PingResult
from chase_core.networking.reporting import (
    HealthRecord,
    ReportContext,
    append_csv_record,
    build_findings,
    build_recommendations,
    health_record_from_ping,
    load_csv_records,
    render_html_report,
    render_text_report,
    summarize_records,
    write_reports,
)


class ReportingTests(unittest.TestCase):
    def test_record_from_ping(self):
        timestamp = datetime(2026, 10, 12, 20, 0, 0)
        up = health_record_from_ping(timestamp, "8.8.8.8", PingResult(True, 15))
        down = health_record_from_ping(timestamp, "8.8.8.8", PingResult(False, None))
        self.assertEqual(up.status, "HEALTHY")
        self.assertEqual(up.packet_loss_pct, 0.0)
        self.assertEqual(down.status, "DOWN")
        self.assertEqual(down.packet_loss_pct, 100.0)

    def test_csv_round_trip_and_summary(self):
        start = datetime(2026, 10, 12, 20, 0, 0)
        records = [
            HealthRecord(start, "8.8.8.8", "HEALTHY", 10, 0.0),
            HealthRecord(start + timedelta(minutes=1), "8.8.8.8", "DOWN", None, 100.0),
            HealthRecord(start + timedelta(minutes=2), "8.8.8.8", "DOWN", None, 100.0),
            HealthRecord(start + timedelta(minutes=3), "8.8.8.8", "DEGRADED", 150, 0.0),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "health.csv"
            for record in records:
                append_csv_record(record, csv_path)

            loaded = load_csv_records(csv_path)
            self.assertEqual(loaded, records)
            summary = summarize_records(loaded)
            self.assertEqual(summary.total_checks, 4)
            self.assertEqual(summary.down_checks, 2)
            self.assertEqual(summary.uptime_pct, 50.0)
            self.assertEqual(summary.packet_loss_pct, 50.0)
            self.assertEqual(summary.average_latency_ms, 80.0)
            self.assertEqual(summary.minimum_latency_ms, 10)
            self.assertEqual(summary.maximum_latency_ms, 150)
            self.assertEqual(summary.downtime_events, 1)
            self.assertEqual(summary.longest_outage_seconds, 120.0)
            self.assertEqual(summary.grade, "POOR")

    def test_target_filter_and_report_rendering(self):
        start = datetime(2026, 10, 12, 20, 0, 0)
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "health.csv"
            append_csv_record(HealthRecord(start, "8.8.8.8", "HEALTHY", 15, 0.0), csv_path)
            append_csv_record(HealthRecord(start, "1.1.1.1", "HEALTHY", 12, 0.0), csv_path)
            filtered = load_csv_records(csv_path, target="8.8.8.8")
            summary = summarize_records(filtered)
            self.assertIn("NETWORK HEALTH DIAGNOSTIC REPORT", render_text_report(summary))
            self.assertIn("Network Health Diagnostic Report", render_html_report(summary))

    def test_customer_context_findings_and_recommendations(self):
        start = datetime(2026, 10, 12, 20, 0, 0)
        records = [
            HealthRecord(start, "8.8.8.8", "HEALTHY", 15, 0.0),
            HealthRecord(start + timedelta(minutes=1), "8.8.8.8", "DOWN", None, 100.0),
            HealthRecord(start + timedelta(minutes=2), "8.8.8.8", "DEGRADED", 145, 0.0),
        ]
        summary = summarize_records(records)
        context = ReportContext(
            client_name="Demo Client",
            site_name="Home Office",
            prepared_by="Network Technician",
            notes="Intermittent connection reported.",
        )
        text = render_text_report(summary, context)
        html = render_html_report(summary, context)

        self.assertIn("Demo Client", text)
        self.assertIn("Home Office", html)
        self.assertIn("FINDINGS", text)
        self.assertIn("RECOMMENDED NEXT STEPS", text)
        self.assertTrue(build_findings(summary))
        self.assertTrue(build_recommendations(summary))
        self.assertIn("Correlate outage timestamps", text)
        self.assertIn("Compare wired and Wi-Fi tests", html)

    def test_write_reports(self):
        start = datetime(2026, 10, 12, 20, 0, 0)
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "health.csv"
            append_csv_record(HealthRecord(start, "8.8.8.8", "HEALTHY", 15, 0.0), csv_path)
            prefix = Path(temp_dir) / "reports" / "health"
            context = ReportContext(client_name="Demo Client")
            text_path, html_path = write_reports(
                csv_path,
                prefix,
                target="8.8.8.8",
                context=context,
            )
            self.assertTrue(text_path.exists())
            self.assertTrue(html_path.exists())
            self.assertIn("Demo Client", text_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
