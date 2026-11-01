"""SQLite storage for test run telemetry."""
import sqlite3
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at REAL NOT NULL,
    finished_at REAL
);
CREATE TABLE IF NOT EXISTS results(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id),
    nodeid TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK(outcome IN ('passed','failed','skipped')),
    duration REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_results_node ON results(nodeid, run_id);
"""


class Store:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)

    def start_run(self, now=None):
        cur = self.conn.execute(
            "INSERT INTO runs(started_at) VALUES(?)", (now or time.time(),))
        self.conn.commit()
        return cur.lastrowid

    def finish_run(self, run_id, now=None):
        self.conn.execute("UPDATE runs SET finished_at=? WHERE id=?",
                          (now or time.time(), run_id))
        self.conn.commit()

    def add_result(self, run_id, nodeid, outcome, duration):
        if outcome not in ("passed", "failed", "skipped"):
            raise ValueError(f"bad outcome: {outcome}")
        if duration < 0:
            raise ValueError("duration must be >= 0")
        self.conn.execute(
            "INSERT INTO results(run_id,nodeid,outcome,duration) VALUES(?,?,?,?)",
            (run_id, nodeid, outcome, duration))
        self.conn.commit()

    def history(self):
        """Return {nodeid: [(run_id, outcome, duration), ...]} ordered by run."""
        rows = self.conn.execute(
            "SELECT nodeid, run_id, outcome, duration FROM results "
            "ORDER BY nodeid, run_id").fetchall()
        out = {}
        for nodeid, run_id, outcome, duration in rows:
            out.setdefault(nodeid, []).append((run_id, outcome, duration))
        return out

    def run_count(self):
        return self.conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]

    def close(self):
        self.conn.close()
