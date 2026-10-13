"""Reusable network-health helpers.

This module contains project-agnostic logic extracted from Network Health Logger.
It has no third-party dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import platform
import re
import subprocess
from typing import Optional


@dataclass(frozen=True)
class PingResult:
    reachable: bool
    latency_ms: Optional[int]


def classify_latency(latency_ms: Optional[int], healthy_max_ms: int = 100) -> str:
    """Convert latency data into a project-defined health status."""
    if latency_ms is None:
        return "DEGRADED"
    return "HEALTHY" if latency_ms <= healthy_max_ms else "DEGRADED"


def _ping_command(target: str, timeout_ms: int) -> list[str]:
    """Build a one-probe ping command for Windows or Unix-like systems."""
    if platform.system().lower() == "windows":
        return ["ping", "-n", "1", "-w", str(timeout_ms), target]

    timeout_seconds = max(1, (timeout_ms + 999) // 1000)
    return ["ping", "-c", "1", "-W", str(timeout_seconds), target]


def _parse_latency_ms(output: str) -> Optional[int]:
    """Extract integer latency from common Windows/Linux ping output."""
    match = re.search(r"time\s*[=<]\s*(\d+(?:\.\d+)?)\s*ms", output, re.IGNORECASE)
    if not match:
        return None
    return max(0, round(float(match.group(1))))


def ping_host(target: str, timeout_ms: int = 1000) -> PingResult:
    """Ping one host once and return normalized reachability and latency.

    Missing ping executables, process-launch failures, and command timeouts are
    normalized to an unreachable result so the logger can fail cleanly.
    """
    process_timeout_seconds = max(2.0, (timeout_ms / 1000) + 1.0)

    try:
        result = subprocess.run(
            _ping_command(target, timeout_ms),
            capture_output=True,
            text=True,
            check=False,
            timeout=process_timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired):
        return PingResult(reachable=False, latency_ms=None)

    if result.returncode != 0:
        return PingResult(reachable=False, latency_ms=None)

    return PingResult(
        reachable=True,
        latency_ms=_parse_latency_ms(result.stdout),
    )


def format_health_line(
    timestamp: str,
    target: str,
    ping: PingResult,
    healthy_max_ms: int = 100,
) -> str:
    """Create the stable text format used by Network Health Logger."""
    if not ping.reachable:
        return f"{timestamp} | {target} | DOWN"

    if ping.latency_ms is None:
        return f"{timestamp} | {target} | latency unavailable | DEGRADED"

    status = classify_latency(ping.latency_ms, healthy_max_ms)
    return f"{timestamp} | {target} | {ping.latency_ms} ms | {status}"


def append_log(message: str, log_file: str | Path) -> None:
    """Append one line to a UTF-8 log file."""
    with Path(log_file).open("a", encoding="utf-8") as file:
        file.write(message + "\n")
