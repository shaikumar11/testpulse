"""Command line: python -m testpulse.cli report --db pulse.db [--fail-on-flaky]"""
import argparse
import sys

from testpulse.metrics import summarize
from testpulse.report import render
from testpulse.store import Store


def main(argv=None):
    p = argparse.ArgumentParser(prog="testpulse")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="print metrics from a telemetry db")
    r.add_argument("--db", default="testpulse.db")
    r.add_argument("--flaky-threshold", type=float, default=0.3)
    r.add_argument("--fail-on-flaky", action="store_true",
                   help="exit 1 when flaky tests exist (CI quality gate)")
    args = p.parse_args(argv)
    store = Store(args.db)
    summary = summarize(store.history(), flaky_threshold=args.flaky_threshold)
    store.close()
    print(render(summary))
    return 1 if args.fail_on_flaky and summary["flaky"] else 0


if __name__ == "__main__":
    sys.exit(main())
