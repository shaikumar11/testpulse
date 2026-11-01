from testpulse.cli import main
from testpulse.metrics import summarize
from testpulse.report import render
from testpulse.store import Store


def seed(path, outcomes):
    s = Store(path)
    for o in outcomes:
        run = s.start_run()
        s.add_result(run, "t::x", o, 0.05)
    s.close()


def test_render_contains_metrics():
    hist = {"t::x": [(1, "passed", 0.05), (2, "failed", 0.07), (3, "passed", 0.06)]}
    text = render(summarize(hist))
    assert "Tests tracked : 1" in text
    assert "Flaky tests   : 1" in text
    assert "t::x" in text


def test_render_empty_suite():
    assert "n/a" in render(summarize({}))


def test_cli_reports_and_gate(tmp_path, capsys):
    db = str(tmp_path / "p.db")
    seed(db, ["passed", "failed", "passed", "failed"])
    assert main(["report", "--db", db]) == 0
    assert "Flaky tests   : 1" in capsys.readouterr().out
    assert main(["report", "--db", db, "--fail-on-flaky"]) == 1


def test_cli_gate_passes_when_stable(tmp_path):
    db = str(tmp_path / "p.db")
    seed(db, ["passed"] * 4)
    assert main(["report", "--db", db, "--fail-on-flaky"]) == 0
