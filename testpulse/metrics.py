"""Metrics computed from stored history: pass rate, p95 latency, flakiness."""
import math


def percentile(values, pct):
    """Nearest-rank percentile. Returns 0.0 for empty input."""
    if not values:
        return 0.0
    if not 0 < pct <= 100:
        raise ValueError("pct must be in (0, 100]")
    ordered = sorted(values)
    rank = math.ceil(pct / 100 * len(ordered))
    return ordered[rank - 1]


def pass_rate(outcomes):
    """Share of passed among executed (skipped ignored). None if nothing ran."""
    ran = [o for o in outcomes if o != "skipped"]
    if not ran:
        return None
    return sum(o == "passed" for o in ran) / len(ran)


def flip_score(outcomes):
    """Flakiness: share of consecutive executed runs whose outcome changed."""
    ran = [o for o in outcomes if o != "skipped"]
    if len(ran) < 2:
        return 0.0
    flips = sum(a != b for a, b in zip(ran, ran[1:]))
    return flips / (len(ran) - 1)


def summarize(history, flaky_threshold=0.3, min_runs=3):
    """Build per-test metrics and suite level totals from Store.history()."""
    tests = []
    for nodeid, rows in history.items():
        outcomes = [r[1] for r in rows]
        durations = [r[2] for r in rows]
        score = flip_score(outcomes)
        tests.append({
            "nodeid": nodeid,
            "runs": len(rows),
            "pass_rate": pass_rate(outcomes),
            "p95": percentile(durations, 95),
            "flip_score": score,
            "flaky": len(rows) >= min_runs and score >= flaky_threshold,
        })
    rates = [t["pass_rate"] for t in tests if t["pass_rate"] is not None]
    return {
        "tests": sorted(tests, key=lambda t: t["nodeid"]),
        "total_tests": len(tests),
        "suite_pass_rate": sum(rates) / len(rates) if rates else None,
        "flaky": [t["nodeid"] for t in tests if t["flaky"]],
        "slowest": sorted(tests, key=lambda t: t["p95"], reverse=True)[:5],
    }
