"""Command-line entrypoint for the Anki Telegram reporter."""

from __future__ import annotations


def main() -> int:
    """Run the CLI.

    The functional report command is implemented in the next SDD phase. Keeping
    this entrypoint importable lets packaging and test tooling validate early.
    """

    print("anki-telegram CLI is installed. The report command is not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
