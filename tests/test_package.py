from anki_telegram import __version__
from anki_telegram.cli import main


def test_package_exposes_version() -> None:
    assert __version__ == "0.1.0"


def test_cli_entrypoint_is_callable(capsys) -> None:
    assert main() == 0
    captured = capsys.readouterr()
    assert "anki-telegram CLI is installed" in captured.out
