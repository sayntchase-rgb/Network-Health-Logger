# Network Health Logger v1.1.0 — Reporting Edition

Version 1.1 turns the original one-probe logger into a small reporting pipeline while preserving the original text output.

## Added

- Structured CSV history in `network_health.csv`
- Per-check target, status, latency, and observed loss fields
- Aggregate uptime and observed packet-loss calculations
- Minimum, average, and maximum latency statistics
- HEALTHY / DEGRADED / DOWN counts
- Downtime event detection
- Longest observed outage window
- Project-defined overall health grade
- Standalone `report_generator.py` command
- TXT and standalone HTML report generation
- Optional automatic report regeneration from `network_health_logger.py --report-prefix ...`
- Reporting unit tests

## Compatibility

The original append-only text log remains available as `network_health.log`.

## Measurement note

Version 1.1 still performs one ICMP probe per logger execution. The CSV therefore records each check as either 0% or 100% observed probe loss, and the report calculates the mean across the selected monitoring period. This is useful for availability tracking but should not be confused with a multi-packet RFC-style packet-loss test.

## Next candidates

Possible later extensions include scheduled continuous monitoring, multi-probe sampling per interval, charts, dashboards, alerts, and multi-target monitoring.
