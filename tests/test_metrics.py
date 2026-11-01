import pytest
from testpulse.metrics import flip_score, pass_rate, percentile, summarize


def test_percentile_nearest_rank():
    assert percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 95) == 10
    assert percentile([1, 2, 3, 4], 50) == 2
    assert percentile([], 95) == 0.0
    with pytest.raises(ValueError):
        percentile([1], 0)


def test_pass_rate_ignores_skips():
    assert pass_rate(["passed", "failed", "skipped", "passed"]) == pytest.approx(2 / 3)
    assert pass_rate(["skipped"]) is None
    assert pass_rate([]) is None


def test_flip_score():
    assert flip_score(["passed"] * 4) == 0.0
    assert flip_score(["passed", "failed", "passed", "failed"]) == 1.0
    assert flip_score(["passed"]) == 0.0
    assert flip_score(["passed", "skipped", "failed"]) == 1.0


def test_summarize_flags_flaky_not_stable_or_new():
    hist = {
        "stable": [(1, "passed", 0.1), (2, "passed", 0.1), (3, "passed", 0.1)],
        "flaky": [(1, "passed", 0.2), (2, "failed", 0.9), (3, "passed", 0.3)],
        "new": [(3, "failed", 0.1)],
    }
    s = summarize(hist)
    assert s["flaky"] == ["flaky"]
    assert s["total_tests"] == 3
    assert s["slowest"][0]["nodeid"] == "flaky"
    assert s["slowest"][0]["p95"] == 0.9


def test_summarize_empty():
    s = summarize({})
    assert s["suite_pass_rate"] is None and s["flaky"] == []
