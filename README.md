# Network Health Logger

A lightweight Python network-monitoring utility that checks reachability, measures latency, classifies network health, stores structured history, and generates customer-readable diagnostic reports.

## Purpose

This project demonstrates practical skills in:

- Python scripting and automation
- Network troubleshooting
- ICMP/ping testing
- Latency measurement
- Structured CSV logging
- Availability and loss analysis
- Customer-facing report generation
- Error handling
- Unit testing
- Git/GitHub workflow
- Technical documentation
- Service productization

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
- Adds optional client, site, technician, and notes metadata
- Generates plain-language findings and suggested next diagnostic steps
- Supports target filtering when generating a report
- Uses reusable helpers in `chase_core`
- Has no third-party Python dependencies

> The default 100 ms HEALTHY threshold, overall report grade, and generated recommendations are project-defined diagnostic aids, not universal networking standards or certifications.

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

Regenerate TXT and HTML reports after a new check:

```powershell
py network_health_logger.py --report-prefix reports\network_health_report
```

This produces:

```text
reports\network_health_report.txt
reports\network_health_report.html
```

## Generate a Customer Diagnostic Report

Basic report from existing history:

```powershell
py report_generator.py
```

Customer-facing example:

```powershell
py report_generator.py `
  --csv-file examples\customer_demo.csv `
  --output-prefix reports\demo_client `
  --target 8.8.8.8 `
  --client-name "Demo Client" `
  --site-name "Home Office" `
  --prepared-by "Network Technician" `
  --notes "Intermittent connection reported."
```

The generated TXT and HTML reports include:

- customer/site metadata
- executive summary
- measured network statistics
- plain-language findings
- suggested next diagnostic steps
- measurement limitations

If one CSV contains multiple targets, filter the report:

```powershell
py report_generator.py --target 8.8.8.8
```

## Productized Service Experiment

`SERVICE_PACKAGE.md` defines the first monetization experiment around this project: a **Network Health Diagnostic** offered at an introductory validation price of **$75**.

The service package includes:

- customer fit/problem definition
- deliverables
- scope boundaries
- intake workflow
- monitoring workflow
- report-generation workflow
- case-study process
- validation metrics
- upgrade path toward recurring monitoring

The goal is to validate one real paid diagnostic before adding a large feature set.

## CSV Format

```csv
timestamp,target,status,latency_ms,packet_loss_pct
2026-10-12 20:01:00,8.8.8.8,HEALTHY,14,0.0
2026-10-12 20:02:00,8.8.8.8,DEGRADED,137,0.0
2026-10-12 20:03:00,8.8.8.8,DOWN,,100.0
```

The current logger still performs one ICMP probe per execution. Each individual row therefore records either `0.0` or `100.0` observed probe loss. Generated reports average those observations across the selected monitoring period to estimate availability/loss behavior.

## Report Metrics

Generated reports include:

- monitoring period
- total checks
- uptime percentage
- observed probe-loss percentage
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

Tests cover core ping normalization and formatting plus CSV persistence, report calculations, target filtering, outage detection, report file generation, customer metadata, findings, and recommendations.

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
├── examples/
│   ├── customer_demo.csv
│   └── README.md
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
├── SERVICE_PACKAGE.md
├── sample_output.txt
├── troubleshooting.md
└── VERSION
```

## Architecture

`network_health_logger.py` remains the live check entry point. Core ping behavior lives in `chase_core/networking/health.py`.

`chase_core/networking/reporting.py` handles structured records, CSV persistence, historical analysis, customer metadata, findings, recommendations, and TXT/HTML rendering. `report_generator.py` provides the command-line entry point for turning existing CSV history into customer-facing reports.

This keeps live network probing separate from analysis and presentation logic.

## Execution Proof

The original logger running successfully in Windows PowerShell:

![Network Health Logger running](screenshots/logger-running.png)

## Scope

The current release does not yet run a permanent background monitoring loop, perform multi-packet sampling per interval, send alerts, host a dashboard, or use a database.

Those are candidates for later validation-driven upgrades rather than being mixed into the first customer diagnostic package.

## Version

Current tagged project version: `1.1.0`.

The customer-diagnostic work is being developed as the next productization increment.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
