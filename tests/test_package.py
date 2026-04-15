from anki_study_telegram_reporter import __version__


def test_package_exposes_version() -> None:
    assert __version__ == "0.1.0"
