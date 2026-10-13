import argparse
from datetime import datetime

from chase_core.networking.health import append_log, format_health_line, ping_host


DEFAULT_TARGET = "8.8.8.8"
DEFAULT_LOG_FILE = "network_health.log"
DEFAULT_TIMEOUT_MS = 1000
DEFAULT_HEALTHY_MAX_MS = 100


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check network reachability, classify latency, and append the result to a log."
    )
    parser.add_argument(
        "--target",
        default=DEFAULT_TARGET,
        help=f"Host or IP address to ping (default: {DEFAULT_TARGET}).",
    )
    parser.add_argument(
        "--log-file",
        default=DEFAULT_LOG_FILE,
        help=f"Log file path (default: {DEFAULT_LOG_FILE}).",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=DEFAULT_TIMEOUT_MS,
        help=f"Ping timeout in milliseconds (default: {DEFAULT_TIMEOUT_MS}).",
    )
    parser.add_argument(
        "--healthy-max-ms",
        type=int,
        default=DEFAULT_HEALTHY_MAX_MS,
        help=(
            "Maximum latency classified as HEALTHY in milliseconds "
            f"(default: {DEFAULT_HEALTHY_MAX_MS})."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    ping = ping_host(args.target, timeout_ms=args.timeout_ms)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = format_health_line(
        timestamp,
        args.target,
        ping,
        healthy_max_ms=args.healthy_max_ms,
    )

    print(message)
    append_log(message, args.log_file)


if __name__ == "__main__":
    main()
