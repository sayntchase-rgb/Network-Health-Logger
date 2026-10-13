# Network Health Logger

A lightweight Python network-monitoring utility that checks reachability, measures latency, classifies network health, stores structured history, and generates customer-readable reports.

## Purpose

This project demonstrates practical skills in:

- Python scripting and automation
- Network troubleshooting
- ICMP/ping testing
- Latency measurement
- Structured CSV logging
- Availability and loss analysis
- Report generation
- Error handling
- Unit testing
- Git/GitHub workflow
- Technical documentation

## Features

- Tests connectivity to a host or IP address
- Measures ping latency
- Classifies each check as `HEALTHY`, `DEGRADED`, or `DOWN`
- Preserves the original human-readable `network_health.log`
- Adds structured `network_health.csv` history
- Calculates uptime and observed probe-loss percentages
- Calculates minimum, average, and maximum latency
- Counts healthy, degraded, and down checks
- Detects downtime events and longest observed outage windows
- Generates TXT and standalone HTML reports
- Supports target filtering when generating a report
- Uses reusable helpers in `chase_core`
- Has no third-party Python dependencies

> The default 100 ms HEALTHY threshold and the overall report grade are project-defined, not universal networking standards.

## Requirements

- Python 3.11+
- A system `ping` command
- Network access for live connectivity checks

## Basic Usage

Run one check with the defaults:

```powershell
py network_health_logger.py
```

By default the program checks `8.8.8.8` and appends data to both:

```text
network_health.log
network_health.csv
```

### Custom target

```powershell
py network_health_logger.py --target 1.1.1.1
```

### Custom threshold and timeout

```powershell
py network_health_logger.py --target 1.1.1.1 --healthy-max-ms 75 --timeout-ms 1500
```

### Custom CSV path

```powershell
py network_health_logger.py --csv-file logs\home_network.csv
```

## Automatic Reporting

Regenerate TXT and HTML reports after the new check:

```powershell
py network_health_logger.py --report-prefix reports\network_health_report
```

This produces:

```text
reports\network_health_report.txt
reports\network_health_report.html
```

## Generate a Report From Existing History

```powershell
py report_generator.py
```

Custom history and output location:

```powershell
py report_generator.py --csv-file logs\home_network.csv --output-prefix reports\home_network
```

If one CSV contains multiple targets, filter the report:

```powershell
py report_generator.py --target 8.8.8.8
```

## CSV Format

```csv
timestamp,target,status,latency_ms,packet_loss_pct
2026-10-12 20:01:00,8.8.8.8,HEALTHY,14,0.0
2026-10-12 20:02:00,8.8.8.8,DEGRADED,137,0.0
2026-10-12 20:03:00,8.8.8.8,DOWN,,100.0
```

Version 1.1 still performs one ICMP probe per execution. Each individual row therefore records either `0.0` or `100.0` observed probe loss. The generated report averages those observations across the selected monitoring period to estimate availability/loss behavior.

## Report Metrics

Generated reports include:

- monitoring period
- total checks
- uptime percentage
- observed packet-loss percentage
- healthy/degraded/down counts
- average latency
- minimum latency
- maximum latency
- downtime-event count
- longest observed outage window
- overall project-defined health grade

## Testing

Run the full unit suite from the repository root:

```powershell
py -m unittest discover -s tests -v
```

The tests cover core ping normalization and formatting plus CSV persistence, report calculations, target filtering, outage detection, and report file generation.

## Project Structure

```text
Network-Health-Logger/
├── .github/
│   └── workflows/
│       └── tests.yml
├── chase_core/
│   ├── __init__.py
│   └── networking/
│       ├── __init__.py
│       ├── health.py
│       └── reporting.py
├── screenshots/
│   └── logger-running.png
├── tests/
│   ├── test_health.py
│   └── test_reporting.py
├── .gitignore
├── LICENSE
├── network_health_logger.py
├── report_generator.py
├── README.md
├── RELEASE_NOTES_v1.0.md
├── RELEASE_NOTES_v1.1.md
├── sample_output.txt
├── troubleshooting.md
└── VERSION
```

## Architecture

`network_health_logger.py` remains the live check entry point. Core ping behavior lives in `chase_core/networking/health.py`.

`chase_core/networking/reporting.py` handles structured records, CSV persistence, historical analysis, and TXT/HTML report rendering. `report_generator.py` provides a separate command-line entry point for turning existing CSV history into reports.

This keeps live network probing separate from analysis and presentation logic.

## Execution Proof

The original logger running successfully in Windows PowerShell:

![Network Health Logger running](screenshots/logger-running.png)

## Scope

Version 1.1 is a reporting-focused release. It does not yet run a permanent background monitoring loop, perform multi-packet sampling per interval, send alerts, host a dashboard, or use a database.

Those remain future extensions rather than being mixed into the reporting milestone.

## Version

Current project version: `1.1.0`.

See `RELEASE_NOTES_v1.1.md` for the current release summary.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
