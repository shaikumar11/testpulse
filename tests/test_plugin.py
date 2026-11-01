"""End to end: run a real pytest session with the plugin and read the telemetry."""
from testpulse.store import Store

pytest_plugins = ["pytester"]

SAMPLE = """
import pytest

def test_ok():
    assert True

def test_bad():
    assert False

@pytest.mark.skip(reason="x")
def test_skip():
    pass
"""


def test_plugin_records_outcomes(pytester):
    pytester.makepyfile(test_sample=SAMPLE)
    db = str(pytester.path / "pulse.db")
    pytester.runpytest_inprocess("-p", "testpulse.plugin", f"--testpulse-db={db}")
    pytester.runpytest_inprocess("-p", "testpulse.plugin", f"--testpulse-db={db}")
    store = Store(db)
    hist = store.history()
    assert store.run_count() == 2
    outcomes = {k.split("::")[-1]: [r[1] for r in v] for k, v in hist.items()}
    assert outcomes["test_ok"] == ["passed", "passed"]
    assert outcomes["test_bad"] == ["failed", "failed"]
    assert outcomes["test_skip"] == ["skipped", "skipped"]
    store.close()
