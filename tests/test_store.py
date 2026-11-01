import pytest
from testpulse.store import Store


def test_runs_and_results_roundtrip():
    s = Store()
    run = s.start_run(now=1.0)
    s.add_result(run, "t::a", "passed", 0.1)
    s.finish_run(run, now=2.0)
    assert s.history() == {"t::a": [(run, "passed", 0.1)]}
    assert s.run_count() == 1


def test_default_timestamps_used():
    s = Store()
    run = s.start_run()
    s.finish_run(run)
    assert s.run_count() == 1


def test_rejects_bad_outcome_and_duration():
    s = Store()
    run = s.start_run()
    with pytest.raises(ValueError):
        s.add_result(run, "t::a", "weird", 0.1)
    with pytest.raises(ValueError):
        s.add_result(run, "t::a", "passed", -1)


def test_history_orders_by_run():
    s = Store()
    for i in range(3):
        run = s.start_run()
        s.add_result(run, "t::a", "passed" if i % 2 == 0 else "failed", 0.01)
    assert [r[1] for r in s.history()["t::a"]] == ["passed", "failed", "passed"]
    s.close()
