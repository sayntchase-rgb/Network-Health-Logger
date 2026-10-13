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


@dataclass(frozen=True)
class ReportContext:
    """Optional customer-facing metadata added to diagnostic reports."""

    client_name: str = ""
    site_name: str = ""
    prepared_by: str = ""
    notes: str = ""


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


def build_findings(summary: ReportSummary) -> list[str]:
    """Translate technical measurements into customer-readable findings."""
    findings = [
        f"Observed availability was {summary.uptime_pct:.2f}% across {summary.total_checks} checks.",
    ]

    if summary.down_checks:
        findings.append(
            f"{summary.down_checks} checks were DOWN across {summary.downtime_events} outage event(s); "
            f"the longest observed outage window was {_format_duration(summary.longest_outage_seconds)}."
        )
    else:
        findings.append("No DOWN checks were observed during the selected monitoring period.")

    if summary.degraded_checks:
        findings.append(
            f"{summary.degraded_checks} checks were DEGRADED, indicating elevated latency or incomplete latency data."
        )
    else:
        findings.append("No DEGRADED checks were observed during the selected monitoring period.")

    if summary.average_latency_ms is not None:
        findings.append(
            "Latency ranged from "
            f"{_format_latency(summary.minimum_latency_ms)} to {_format_latency(summary.maximum_latency_ms)}, "
            f"with an average of {_format_latency(summary.average_latency_ms)}."
        )
    else:
        findings.append("No successful latency measurements were available for this report.")

    return findings


def build_recommendations(summary: ReportSummary) -> list[str]:
    """Return conservative next-step recommendations based on the observed data."""
    recommendations: list[str] = []

    if summary.down_checks:
        recommendations.append(
            "Correlate outage timestamps with modem/router logs and ISP status to identify whether failures are local or upstream."
        )
    if summary.degraded_checks:
        recommendations.append(
            "Compare wired and Wi-Fi tests during degraded periods to separate internet-path issues from local wireless interference."
        )
    if summary.maximum_latency_ms is not None and summary.maximum_latency_ms >= 100:
        recommendations.append(
            "Run multi-probe latency tests during high-latency periods to confirm whether spikes are persistent or isolated."
        )
    if summary.total_checks < 20:
        recommendations.append(
            "Collect a longer monitoring sample before making strong reliability conclusions; this report contains fewer than 20 checks."
        )
    if not recommendations:
        recommendations.append(
            "Continue periodic monitoring to establish a longer baseline and make intermittent changes easier to detect."
        )

    return recommendations


def _context_text_lines(context: ReportContext | None) -> list[str]:
    if context is None:
        return []

    fields = [
        ("Client", context.client_name),
        ("Site", context.site_name),
        ("Prepared by", context.prepared_by),
    ]
    lines = [f"{label + ':':<20}{value}" for label, value in fields if value.strip()]
    if context.notes.strip():
        lines.extend(["", "Customer / technician notes:", context.notes.strip()])
    return lines


def render_text_report(
    summary: ReportSummary,
    context: ReportContext | None = None,
) -> str:
    """Render a plain-text customer-readable diagnostic report."""
    findings = build_findings(summary)
    recommendations = build_recommendations(summary)
    context_lines = _context_text_lines(context)

    lines = [
        "NETWORK HEALTH DIAGNOSTIC REPORT",
        "================================",
    ]
    if context_lines:
        lines.extend(context_lines)
        lines.append("")

    lines.extend(
        [
            f"Target:              {summary.target}",
            f"Period start:        {summary.start_time.strftime(TIMESTAMP_FORMAT)}",
            f"Period end:          {summary.end_time.strftime(TIMESTAMP_FORMAT)}",
            f"Total checks:        {summary.total_checks}",
            "",
            "EXECUTIVE SUMMARY",
            "-----------------",
            f"Overall health:      {summary.grade}",
            f"Uptime:              {summary.uptime_pct:.2f}%",
            f"Observed packet loss:{summary.packet_loss_pct:>9.2f}%",
            "",
            "MEASUREMENTS",
            "------------",
            f"Healthy checks:      {summary.healthy_checks}",
            f"Degraded checks:     {summary.degraded_checks}",
            f"Down checks:         {summary.down_checks}",
            f"Average latency:     {_format_latency(summary.average_latency_ms)}",
            f"Minimum latency:     {_format_latency(summary.minimum_latency_ms)}",
            f"Maximum latency:     {_format_latency(summary.maximum_latency_ms)}",
            f"Downtime events:     {summary.downtime_events}",
            f"Longest outage:      {_format_duration(summary.longest_outage_seconds)}",
            "",
            "FINDINGS",
            "--------",
        ]
    )
    lines.extend(f"- {finding}" for finding in findings)
    lines.extend(["", "RECOMMENDED NEXT STEPS", "----------------------"])
    lines.extend(f"- {recommendation}" for recommendation in recommendations)
    lines.extend(
        [
            "",
            "MEASUREMENT NOTE",
            "----------------",
            "Packet loss is estimated from failed one-probe checks across the report period.",
            "The health grade and recommendations are project-defined diagnostic aids, not industry certifications.",
            "",
        ]
    )
    return "\n".join(lines)


def _html_context(context: ReportContext | None) -> str:
    if context is None:
        return ""

    rows = []
    for label, value in (
        ("Client", context.client_name),
        ("Site", context.site_name),
        ("Prepared by", context.prepared_by),
    ):
        if value.strip():
            rows.append(
                f"<tr><th>{escape(label)}</th><td>{escape(value.strip())}</td></tr>"
            )
    notes = ""
    if context.notes.strip():
        notes = (
            '<div class="notes"><h2>Customer / Technician Notes</h2>'
            f"<p>{escape(context.notes.strip())}</p></div>"
        )
    if not rows and not notes:
        return ""

    table = ""
    if rows:
        table = '<table class="meta">' + "\n".join(rows) + "</table>"
    return f'<section class="context">{table}{notes}</section>'


def render_html_report(
    summary: ReportSummary,
    context: ReportContext | None = None,
) -> str:
    """Render a standalone customer-facing HTML diagnostic report."""
    target = escape(summary.target)
    findings = "".join(f"<li>{escape(item)}</li>" for item in build_findings(summary))
    recommendations = "".join(
        f"<li>{escape(item)}</li>" for item in build_recommendations(summary)
    )
    context_html = _html_context(context)

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
    ]
    table_rows = "\n".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in rows
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Network Health Diagnostic Report - {target}</title>
<style>
:root {{ color-scheme: light; }}
body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px 48px; line-height: 1.5; color: #1f2933; }}
h1 {{ margin-bottom: 4px; }}
h2 {{ margin-top: 30px; }}
.subtitle {{ margin-top: 0; color: #52606d; }}
.grade {{ display: inline-block; padding: 8px 12px; border: 1px solid #bcccdc; border-radius: 6px; font-weight: 700; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
th, td {{ text-align: left; border-bottom: 1px solid #d9e2ec; padding: 10px 8px; vertical-align: top; }}
th {{ width: 45%; }}
.context {{ margin: 24px 0; }}
.meta {{ max-width: 640px; }}
.notes {{ margin-top: 18px; }}
ul {{ padding-left: 24px; }}
.note {{ margin-top: 30px; padding-top: 16px; border-top: 1px solid #d9e2ec; font-size: 0.9rem; color: #52606d; }}
</style>
</head>
<body>
<h1>Network Health Diagnostic Report</h1>
<p class="subtitle">Customer-facing summary generated by Network Health Logger.</p>
{context_html}
<h2>Executive Summary</h2>
<p class="grade">Overall health: {escape(summary.grade)}</p>
<p>Observed uptime was <strong>{summary.uptime_pct:.2f}%</strong> across {summary.total_checks} checks, with {summary.packet_loss_pct:.2f}% estimated probe loss.</p>
<h2>Measurements</h2>
<table>
{table_rows}
</table>
<h2>Findings</h2>
<ul>{findings}</ul>
<h2>Recommended Next Steps</h2>
<ul>{recommendations}</ul>
<p class="note">Packet loss is estimated from failed one-probe checks across the report period. The health grade and recommendations are project-defined diagnostic aids, not industry certifications.</p>
</body>
</html>
"""


def write_reports(
    csv_file: str | Path,
    output_prefix: str | Path = "network_health_report",
    target: str | None = None,
    context: ReportContext | None = None,
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
    text_path.write_text(render_text_report(summary, context=context), encoding="utf-8")
    html_path.write_text(render_html_report(summary, context=context), encoding="utf-8")
    return text_path, html_path
