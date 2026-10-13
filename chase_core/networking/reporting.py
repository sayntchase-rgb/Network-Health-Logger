"""Structured logging and reporting helpers for Network Health Logger."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from statistics import mean
from typing import Iterable, Optional

from .health import PingResult, classify_latency

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
CSV_FIELDS = ("timestamp", "target", "status", "latency_ms", "packet_loss_pct")


@dataclass(frozen=True)
class HealthRecord:
    timestamp: datetime
    target: str
    status: str
    latency_ms: Optional[int]
    packet_loss_pct: float


@dataclass(frozen=True)
class ReportSummary:
    target: str
    start_time: datetime
    end_time: datetime
    total_checks: int
    healthy_checks: int
    degraded_checks: int
    down_checks: int
    uptime_pct: float
    packet_loss_pct: float
    average_latency_ms: Optional[float]
    minimum_latency_ms: Optional[int]
    maximum_latency_ms: Optional[int]
    downtime_events: int
    longest_outage_seconds: float
    grade: str


def health_record_from_ping(
    timestamp: datetime,
    target: str,
    ping: PingResult,
    healthy_max_ms: int = 100,
) -> HealthRecord:
    """Convert a single ping result into a structured record."""
    if not ping.reachable:
        status = "DOWN"
        packet_loss_pct = 100.0
    else:
        status = classify_latency(ping.latency_ms, healthy_max_ms)
        packet_loss_pct = 0.0

    return HealthRecord(
        timestamp=timestamp,
        target=target,
        status=status,
        latency_ms=ping.latency_ms,
        packet_loss_pct=packet_loss_pct,
    )


def append_csv_record(record: HealthRecord, csv_file: str | Path) -> None:
    """Append a structured record, creating the CSV header when needed."""
    path = Path(csv_file)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)

    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": record.timestamp.strftime(TIMESTAMP_FORMAT),
                "target": record.target,
                "status": record.status,
                "latency_ms": "" if record.latency_ms is None else record.latency_ms,
                "packet_loss_pct": f"{record.packet_loss_pct:.1f}",
            }
        )


def load_csv_records(
    csv_file: str | Path,
    target: str | None = None,
) -> list[HealthRecord]:
    """Load records from a CSV file, optionally filtering by target."""
    path = Path(csv_file)
    if not path.exists():
        return []

    records: list[HealthRecord] = []
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        missing = [field for field in CSV_FIELDS if field not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV is missing required fields: {', '.join(missing)}")

        for row in reader:
            row_target = row["target"].strip()
            if target is not None and row_target != target:
                continue

            latency_text = row["latency_ms"].strip()
            records.append(
                HealthRecord(
                    timestamp=datetime.strptime(row["timestamp"].strip(), TIMESTAMP_FORMAT),
                    target=row_target,
                    status=row["status"].strip().upper(),
                    latency_ms=int(latency_text) if latency_text else None,
                    packet_loss_pct=float(row["packet_loss_pct"]),
                )
            )

    return sorted(records, key=lambda record: record.timestamp)


def _outage_stats(records: list[HealthRecord]) -> tuple[int, float]:
    events = 0
    longest_seconds = 0.0
    outage_start: datetime | None = None

    for record in records:
        if record.status == "DOWN" and outage_start is None:
            events += 1
            outage_start = record.timestamp
        elif record.status != "DOWN" and outage_start is not None:
            longest_seconds = max(
                longest_seconds,
                (record.timestamp - outage_start).total_seconds(),
            )
            outage_start = None

    if outage_start is not None:
        longest_seconds = max(
            longest_seconds,
            (records[-1].timestamp - outage_start).total_seconds(),
        )

    return events, max(0.0, longest_seconds)


def _grade_network(uptime_pct: float, packet_loss_pct: float) -> str:
    """Return a simple project-defined overall grade."""
    if uptime_pct >= 99.9 and packet_loss_pct <= 0.1:
        return "EXCELLENT"
    if uptime_pct >= 99.0 and packet_loss_pct <= 1.0:
        return "GOOD"
    if uptime_pct >= 95.0:
        return "FAIR"
    return "POOR"


def summarize_records(records: Iterable[HealthRecord]) -> ReportSummary:
    """Calculate availability, latency, loss, and outage statistics."""
    ordered = sorted(records, key=lambda record: record.timestamp)
    if not ordered:
        raise ValueError("No health records are available to summarize.")

    targets = sorted({record.target for record in ordered})
    if len(targets) != 1:
        raise ValueError("Report data must contain exactly one target. Filter by target first.")

    total = len(ordered)
    healthy = sum(record.status == "HEALTHY" for record in ordered)
    degraded = sum(record.status == "DEGRADED" for record in ordered)
    down = sum(record.status == "DOWN" for record in ordered)
    reachable = total - down
    latencies = [record.latency_ms for record in ordered if record.latency_ms is not None]
    events, longest_seconds = _outage_stats(ordered)
    uptime_pct = (reachable / total) * 100
    packet_loss_pct = mean(record.packet_loss_pct for record in ordered)

    return ReportSummary(
        target=targets[0],
        start_time=ordered[0].timestamp,
        end_time=ordered[-1].timestamp,
        total_checks=total,
        healthy_checks=healthy,
        degraded_checks=degraded,
        down_checks=down,
        uptime_pct=uptime_pct,
        packet_loss_pct=packet_loss_pct,
        average_latency_ms=mean(latencies) if latencies else None,
        minimum_latency_ms=min(latencies) if latencies else None,
        maximum_latency_ms=max(latencies) if latencies else None,
        downtime_events=events,
        longest_outage_seconds=longest_seconds,
        grade=_grade_network(uptime_pct, packet_loss_pct),
    )


def _format_latency(value: Optional[float]) -> str:
    return "N/A" if value is None else f"{value:.1f} ms"


def _format_duration(seconds: float) -> str:
    seconds = max(0, round(seconds))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def render_text_report(summary: ReportSummary) -> str:
    """Render a plain-text customer-readable report."""
    return "\n".join(
        [
            "NETWORK HEALTH REPORT",
            "=====================",
            f"Target:              {summary.target}",
            f"Period start:        {summary.start_time.strftime(TIMESTAMP_FORMAT)}",
            f"Period end:          {summary.end_time.strftime(TIMESTAMP_FORMAT)}",
            f"Total checks:        {summary.total_checks}",
            "",
            f"Uptime:              {summary.uptime_pct:.2f}%",
            f"Observed packet loss:{summary.packet_loss_pct:>9.2f}%",
            f"Healthy checks:      {summary.healthy_checks}",
            f"Degraded checks:     {summary.degraded_checks}",
            f"Down checks:         {summary.down_checks}",
            "",
            f"Average latency:     {_format_latency(summary.average_latency_ms)}",
            f"Minimum latency:     {_format_latency(summary.minimum_latency_ms)}",
            f"Maximum latency:     {_format_latency(summary.maximum_latency_ms)}",
            "",
            f"Downtime events:     {summary.downtime_events}",
            f"Longest outage:      {_format_duration(summary.longest_outage_seconds)}",
            f"Overall health:      {summary.grade}",
            "",
            "Note: packet loss is estimated from failed one-probe checks across the report period.",
            "The health grade is project-defined and is not a networking industry standard.",
            "",
        ]
    )


def render_html_report(summary: ReportSummary) -> str:
    """Render a standalone HTML report with no external dependencies."""
    target = escape(summary.target)
    rows = [
        ("Target", target),
        ("Period start", summary.start_time.strftime(TIMESTAMP_FORMAT)),
        ("Period end", summary.end_time.strftime(TIMESTAMP_FORMAT)),
        ("Total checks", str(summary.total_checks)),
        ("Uptime", f"{summary.uptime_pct:.2f}%"),
        ("Observed packet loss", f"{summary.packet_loss_pct:.2f}%"),
        ("Healthy checks", str(summary.healthy_checks)),
        ("Degraded checks", str(summary.degraded_checks)),
        ("Down checks", str(summary.down_checks)),
        ("Average latency", _format_latency(summary.average_latency_ms)),
        ("Minimum latency", _format_latency(summary.minimum_latency_ms)),
        ("Maximum latency", _format_latency(summary.maximum_latency_ms)),
        ("Downtime events", str(summary.downtime_events)),
        ("Longest outage", _format_duration(summary.longest_outage_seconds)),
        ("Overall health", summary.grade),
    ]
    table_rows = "\n".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in rows
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Network Health Report - {target}</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 820px; margin: 40px auto; padding: 0 20px; line-height: 1.45; }}
h1 {{ margin-bottom: 4px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 24px; }}
th, td {{ text-align: left; border-bottom: 1px solid #ddd; padding: 10px 8px; }}
th {{ width: 45%; }}
.note {{ margin-top: 24px; font-size: 0.9rem; }}
</style>
</head>
<body>
<h1>Network Health Report</h1>
<p>Structured summary generated by Network Health Logger.</p>
<table>
{table_rows}
</table>
<p class="note">Packet loss is estimated from failed one-probe checks across the report period. The health grade is project-defined and is not an industry standard.</p>
</body>
</html>
"""


def write_reports(
    csv_file: str | Path,
    output_prefix: str | Path = "network_health_report",
    target: str | None = None,
) -> tuple[Path, Path]:
    """Build text and HTML reports from structured CSV history."""
    records = load_csv_records(csv_file, target=target)
    if not records:
        raise ValueError("No matching records were found in the CSV file.")

    summary = summarize_records(records)
    prefix = Path(output_prefix)
    if prefix.parent != Path("."):
        prefix.parent.mkdir(parents=True, exist_ok=True)

    text_path = prefix.with_suffix(".txt")
    html_path = prefix.with_suffix(".html")
    text_path.write_text(render_text_report(summary), encoding="utf-8")
    html_path.write_text(render_html_report(summary), encoding="utf-8")
    return text_path, html_path
