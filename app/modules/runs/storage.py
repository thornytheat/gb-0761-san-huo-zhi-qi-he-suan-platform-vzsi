import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.errors import Rejected


@contextmanager
def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=15)
    try:
        db.execute("CREATE TABLE IF NOT EXISTS harbor_runs (id TEXT PRIMARY KEY, snapshot TEXT NOT NULL)")
        with db:
            yield db
    finally:
        db.close()


def commit(path, manifest):
    with connect(path) as db:
        run_id = manifest["run_id"]
        inserted = db.execute("INSERT OR IGNORE INTO harbor_runs VALUES (?, ?)", (run_id, json.dumps(manifest))).rowcount == 1
        payload, = db.execute("SELECT snapshot FROM harbor_runs WHERE id = ?", (run_id,)).fetchone()
        return json.loads(payload), inserted


def lookup(path, run_id):
    with connect(path) as db:
        result = db.execute("SELECT snapshot FROM harbor_runs WHERE id = ?", (run_id,)).fetchone()
        if not result:
            raise Rejected("UNKNOWN_RUN", status=404)
        return json.loads(result[0])


def list_runs(path):
    with connect(path) as db:
        return [json.loads(row[0]) for row in db.execute("SELECT snapshot FROM harbor_runs ORDER BY rowid DESC LIMIT 50")]
