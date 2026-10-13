# Network Health Logger

A lightweight Python network-monitoring utility that checks reachability, measures latency, classifies network health, and records timestamped historical results.

## Purpose

This project was built to practice and demonstrate practical skills in:

- Python scripting
- Network troubleshooting
- ICMP/ping testing
- Latency measurement
- Process return-code handling
- Error handling
- File logging
- Unit testing
- Git version control
- Technical documentation

## Features

- Tests connectivity to a host or IP address
- Measures ping latency
- Classifies network status as:
  - `HEALTHY` — latency at or below the configured threshold
  - `DEGRADED` — latency above the threshold, or latency cannot be parsed
  - `DOWN` — ping fails, times out, or cannot be launched
- Adds timestamps to each result
- Stores historical results in a local log
- Supports configurable target, timeout, health threshold, and log path
- Uses reusable network-health helpers in `chase_core`
- Includes unit tests and execution proof
- Has no third-party Python dependencies

> The default 100 ms threshold is project-defined and is not intended as a universal networking standard.

## Example Output

```text
2026-10-07 06:51:43 | 8.8.8.8 | 15 ms | HEALTHY
2026-10-07 06:52:34 | 8.8.8.8 | 11 ms | HEALTHY
2026-10-07 06:53:12 | 8.8.8.8 | DOWN
```

## Requirements

- Python 3.11+
- A system `ping` command
- Network access for live connectivity checks

The project uses only the Python standard library.

## Usage

Run with the defaults:

```powershell
py network_health_logger.py
```

The default target is `8.8.8.8`, the default HEALTHY threshold is `100 ms`, and results are appended to `network_health.log`.

### Custom target

```powershell
py network_health_logger.py --target 1.1.1.1
```

### Custom health threshold and timeout

```powershell
py network_health_logger.py --target 1.1.1.1 --healthy-max-ms 75 --timeout-ms 1500
```

### Custom log file

```powershell
py network_health_logger.py --log-file logs\home_network.log
```

Show all options:

```powershell
py network_health_logger.py --help
```

## Testing

Run the unit suite from the repository root:

```powershell
py -m unittest discover -s tests -v
```

The tests cover health classification, latency parsing, command construction, output formatting, clean handling of a missing ping executable, successful ping normalization, and file logging.

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
│       └── health.py
├── screenshots/
│   └── logger-running.png
├── tests/
│   └── test_health.py
├── .gitignore
├── LICENSE
├── network_health_logger.py
├── README.md
├── RELEASE_NOTES_v1.0.md
├── sample_output.txt
├── troubleshooting.md
└── VERSION
```

## Architecture

`network_health_logger.py` is the command-line entry point. Reusable networking logic lives in `chase_core/networking/health.py`, which handles ping command construction, latency parsing, status classification, stable output formatting, and log writing.

This separation keeps the CLI small and makes the core behavior directly testable.

## Troubleshooting Case Study

`troubleshooting.md` documents a hands-on Windows networking investigation using `ipconfig`, `ping`, `nslookup`, `tracert`, and `arp -a` to isolate IPv4, DNS, routing, and IPv6 behavior.

## Execution Proof

The logger running successfully in Windows PowerShell:

![Network Health Logger running](screenshots/logger-running.png)

## Skills Demonstrated

- Python automation
- TCP/IP troubleshooting
- ICMP diagnostics
- Cross-platform command handling
- Defensive error handling
- Unit testing
- Modular code organization
- File-based logging
- Git/GitHub workflow
- Technical documentation

## Scope

Version 1.0 is intentionally small: one probe per execution, one normalized result, and one append-only local log. Continuous scheduling, dashboards, databases, alerts, and multi-target monitoring are possible future extensions, but they are outside the v1.0 scope.

## Version

Current project version: `1.0.0`.

See `RELEASE_NOTES_v1.0.md` for the v1.0 release summary.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
