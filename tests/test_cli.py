from anki_telegram.cli import main


def test_report_mock_dry_run_outputs_message(capsys) -> None:
    result = main(["report", "--source", "mock", "--date", "2026-04-15", "--dry-run"])

    assert result == 0
    captured = capsys.readouterr()
    assert "Anki 今日戰報 2026-04-15" in captured.out
    assert "答題數：132 / 100" in captured.out
    assert "重新學習：0" in captured.out


def test_ankiweb_source_requires_credentials_without_local_env(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ANKI_USERNAME", raising=False)
    monkeypatch.delenv("ANKI_PASSWORD", raising=False)

    result = main(["report", "--source", "ankiweb", "--dry-run"])

    assert result == 2
    captured = capsys.readouterr()
    assert "ANKI_USERNAME" in captured.err
