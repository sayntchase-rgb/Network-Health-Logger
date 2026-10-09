# Network Health Logger

[![Tests](https://github.com/sayntchase-rgb/Network-Health-Logger/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/sayntchase-rgb/Network-Health-Logger/actions/workflows/tests.yml)



A lightweight Python network-monitoring utility that checks connectivity, measures latency, classifies network health, and records timestamped historical results.



## Purpose



This project was built to practice and demonstrate practical skills in:



- Python scripting

- Network troubleshooting

- ICMP/ping testing

- Latency measurement

- Process return-code handling

- File logging

- Git version control

- Technical documentation



## Features



- Tests connectivity to a network target

- Measures ping latency

- Classifies network status as:

&#x20; - `HEALTHY` — latency of 100 ms or less

&#x20; - `DEGRADED` — latency above 100 ms or unavailable

&#x20; - `DOWN` — ping test fails

- Adds timestamps to each result

- Stores historical results in a local log

- Includes sample monitoring output for review



> The 100 ms threshold is a project-defined threshold and is not intended as a universal networking standard.



## Example Output



```text

2026-10-07 06:51:43 | 8.8.8.8 | 15 ms | HEALTHY

2026-10-07 06:52:34 | 8.8.8.8 | 11 ms | HEALTHY

2026-10-07 06:52:34 | 8.8.8.8 | 10 ms | HEALTHY

```



## Requirements



- Windows

- Python 3

- Network connectivity



Developed using Python 3.11.9.



## Usage



Run from PowerShell:



```powershell

py network_health_logger.py

```



The program displays the current result and appends it to:



```text

network_health.log

```



Runtime log files are excluded from Git using `.gitignore`. A static example is included in `sample_output.txt`.



## Automated Tests

From the repository folder, run in PowerShell:

```powershell
py -m unittest discover -s tests -v
```

If your Python command is `python`, use `python -m unittest discover -s tests -v`.
No additional packages are needed: the tests use Python's built-in `unittest`.

The eight tests cover healthy replies, the inclusive 100 ms boundary, degraded
latency, unavailable latency, failed pings, timestamped console/file output,
and appending without overwriting earlier log entries. They also preserve the
current behavior of displaying `time<1ms` as `1 ms`.

Tests simulate ping responses and use a fixed clock and temporary log files.
They do not send network traffic or modify your real `network_health.log`.
These tests verify the script's behavior, not live connectivity or Windows ping itself.

The **Tests** GitHub Actions workflow runs the same test command on Windows with
Python 3.11 for every push and pull request. The badge above shows the latest
workflow status on `main`; click it to inspect runs and any failures.

## Project Structure



```text
Network-Health-Logger/
├── .github/workflows/tests.yml
├── tests/test_network_health_logger.py
├── screenshots/logger-running.png
├── network_health_logger.py
├── sample_output.txt
├── troubleshooting.md
├── README.md
└── .gitignore
```



## Skills Demonstrated



This project demonstrates basic network diagnostics, Python automation, structured troubleshooting, logging, documentation, and Git-based development.


## Execution Proof

The logger running successfully in Windows PowerShell:

![Network Health Logger running](screenshots/logger-running.png)
