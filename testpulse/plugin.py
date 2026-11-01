"""pytest plugin: records every test result into a TestPulse SQLite database.

Usage: pytest -p testpulse.plugin --testpulse-db=pulse.db
State lives on a per session recorder, so nested or parallel sessions never clash.
"""
from testpulse.store import Store


def pytest_addoption(parser):
    parser.addoption("--testpulse-db", default="testpulse.db",
                     help="SQLite file for test telemetry")


def outcome_of(report):
    """Map a pytest report to passed, failed or skipped."""
    if report.skipped:
        return "skipped"
    return "passed" if report.passed else "failed"


def should_record(report):
    """Record the call phase, plus setup phase failures and skips."""
    return report.when == "call" or (report.when == "setup" and not report.passed)


class Recorder:
    def __init__(self, db_path):
        self.store = Store(db_path)
        self.run_id = self.store.start_run()

    def pytest_runtest_logreport(self, report):
        if should_record(report):
            self.store.add_result(
                self.run_id, report.nodeid, outcome_of(report), report.duration)

    def pytest_sessionfinish(self, session):
        self.store.finish_run(self.run_id)
        self.store.close()


def pytest_configure(config):
    config.pluginmanager.register(
        Recorder(config.getoption("--testpulse-db")), "testpulse-recorder")
