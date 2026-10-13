import argparse

from chase_core.networking.reporting import ReportContext, write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate customer-facing TXT and HTML network diagnostic reports."
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
    parser.add_argument(
        "--client-name",
        default="",
        help="Optional customer or organization name shown on the report.",
    )
    parser.add_argument(
        "--site-name",
        default="",
        help="Optional site, office, or location label shown on the report.",
    )
    parser.add_argument(
        "--prepared-by",
        default="",
        help="Optional technician or analyst name shown on the report.",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional customer or technician notes included in the report.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    context = ReportContext(
        client_name=args.client_name,
        site_name=args.site_name,
        prepared_by=args.prepared_by,
        notes=args.notes,
    )

    try:
        text_path, html_path = write_reports(
            args.csv_file,
            output_prefix=args.output_prefix,
            target=args.target,
            context=context,
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error

    print(f"Created: {text_path}")
    print(f"Created: {html_path}")


if __name__ == "__main__":
    main()
