"""Command-line entrypoint for the Anki Telegram reporter."""

from __future__ import annotations

import argparse
from datetime import date
import sys

from .config import ConfigError, build_config
from .logging import redact
from .renderer import render_report
from .sources import SourceError, load_metrics
from .telegram import TelegramClient, TelegramError


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
        message = render_report(
            metrics,
            vocabulary_target_count=config.vocabulary_target_count,
            exam_date=config.exam_date,
            report_slot=config.report_slot,
            supervisor_usernames=config.supervisor_usernames,
        )
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    except SourceError as exc:
        print(f"error: {redact(str(exc), _known_secrets())}", file=sys.stderr)
        return 2

    if config.dry_run:
        print(message)
        return 0

    try:
        TelegramClient(
            bot_token=config.telegram_bot_token or "",
            chat_id=config.telegram_chat_id or "",
            thread_id=config.telegram_thread_id,
        ).send_message(message)
    except TelegramError as exc:
        print(f"error: {redact(str(exc), _known_secrets())}", file=sys.stderr)
        return 2

    print("Telegram report sent.")
    return 0


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


def _known_secrets() -> list[str | None]:
    import os

    return [
        os.environ.get("ANKI_PASSWORD"),
        os.environ.get("TELEGRAM_BOT_TOKEN"),
    ]


if __name__ == "__main__":
    raise SystemExit(main())
