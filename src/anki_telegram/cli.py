"""Command-line entrypoint for the Anki Telegram reporter."""

from __future__ import annotations

import argparse
from datetime import date
import sys

from .config import ConfigError, build_config
from .renderer import render_report
from .sources import SourceError, load_metrics


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "report":
        return _run_report(args)

    parser.print_help()
    return 0


def _run_report(args: argparse.Namespace) -> int:
    try:
        config = build_config(
            source=args.source,
            dry_run=args.dry_run,
            send=args.send,
            report_date=args.report_date,
        )
        metrics = load_metrics(config)
        message = render_report(metrics)
    except (ConfigError, SourceError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if config.dry_run:
        print(message)
        return 0

    print("error: Telegram delivery is not implemented yet.", file=sys.stderr)
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="anki-telegram")
    subparsers = parser.add_subparsers(dest="command")

    report = subparsers.add_parser("report", help="Generate and optionally send a daily study report.")
    report.add_argument("--source", choices=["mock", "ankiweb"], help="Study data source.")
    report.add_argument("--date", dest="report_date", type=date.fromisoformat, help="Report date in YYYY-MM-DD.")

    send_mode = report.add_mutually_exclusive_group()
    send_mode.add_argument("--dry-run", action="store_true", default=None, help="Print the message without sending.")
    send_mode.add_argument("--send", action="store_true", help="Send the message to Telegram.")

    return parser


if __name__ == "__main__":
    raise SystemExit(main())
