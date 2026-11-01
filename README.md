# TestPulse

Test telemetry for pytest. A plugin records every test outcome and duration into SQLite across runs,
then computes pass rate, p95 duration and a flakiness score (outcome flips between consecutive runs).
The CLI prints a report and can fail CI when flaky tests exist.

## Use
    pip install -r requirements.txt
    pytest -p testpulse.plugin --testpulse-db=pulse.db
    python -m testpulse.cli report --db pulse.db --fail-on-flaky

## Test and coverage
    coverage run --source=testpulse -m pytest -p testpulse.plugin --testpulse-db=pulse.db
    coverage report -m --fail-under=90

CI (GitHub Actions) enforces the 90% coverage gate and prints the telemetry report.
