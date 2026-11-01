"""Plain text report renderer."""


def render(summary):
    lines = ["TestPulse report", "=" * 16,
             f"Tests tracked : {summary['total_tests']}"]
    rate = summary["suite_pass_rate"]
    lines.append("Suite pass rate: " + ("n/a" if rate is None else f"{rate:.1%}"))
    lines.append(f"Flaky tests   : {len(summary['flaky'])}")
    for nodeid in summary["flaky"]:
        lines.append(f"  - {nodeid}")
    lines.append("Slowest by p95:")
    for t in summary["slowest"]:
        lines.append(f"  {t['p95'] * 1000:8.1f} ms  {t['nodeid']}")
    return "\n".join(lines)
