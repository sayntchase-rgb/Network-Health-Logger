import argparse
from datetime import datetime

from chase_core.networking.health import append_log, format_health_line, ping_host
from chase_core.networking.reporting import (
    append_csv_record,
    health_record_from_ping,
    write_reports,
)


DEFAULT_TARGET = "8.8.8.8"
DEFAULT_LOG_FILE = "network_health.log"
DEFAULT_CSV_FILE = "network_health.csv"
DEFAULT_TIMEOUT_MS = 1000
DEFAULT_HEALTHY_MAX_MS = 100


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check network health, log structured history, and optionally generate reports."
    )
    parser.add_argument(
        "--target",
        default=DEFAULT_TARGET,
        help=f"Host or IP address to ping (default: {DEFAULT_TARGET}).",
    )
    parser.add_argument(
        "--log-file",
        default=DEFAULT_LOG_FILE,
        help=f"Legacy text log path (default: {DEFAULT_LOG_FILE}).",
    )
    parser.add_argument(
        "--csv-file",
        default=DEFAULT_CSV_FILE,
        help=f"Structured CSV history path (default: {DEFAULT_CSV_FILE}).",
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
    parser.add_argument(
        "--report-prefix",
        default=None,
        help="Optional output prefix for automatic TXT and HTML reports.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    ping = ping_host(args.target, timeout_ms=args.timeout_ms)
    timestamp = datetime.now()
    timestamp_text = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    message = format_health_line(
        timestamp_text,
        args.target,
        ping,
        healthy_max_ms=args.healthy_max_ms,
    )

    print(message)
    append_log(message, args.log_file)

    record = health_record_from_ping(
        timestamp,
        args.target,
        ping,
        healthy_max_ms=args.healthy_max_ms,
    )
    append_csv_record(record, args.csv_file)

    if args.report_prefix:
        text_path, html_path = write_reports(
            args.csv_file,
            output_prefix=args.report_prefix,
            target=args.target,
        )
        print(f"Report: {text_path}")
        print(f"Report: {html_path}")


if __name__ == "__main__":
    main()
