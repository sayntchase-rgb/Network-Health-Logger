import argparse

from chase_core.networking.reporting import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate TXT and HTML summaries from Network Health Logger CSV history."
    )
    parser.add_argument(
        "--csv-file",
        default="network_health.csv",
        help="Structured CSV history to analyze.",
    )
    parser.add_argument(
        "--output-prefix",
        default="network_health_report",
        help="Output path prefix; .txt and .html are created automatically.",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Optional target filter when the CSV contains more than one target.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        text_path, html_path = write_reports(
            args.csv_file,
            output_prefix=args.output_prefix,
            target=args.target,
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error

    print(f"Created: {text_path}")
    print(f"Created: {html_path}")


if __name__ == "__main__":
    main()
