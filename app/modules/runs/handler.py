from flask import Blueprint, current_app

from app.input import read_sources
from .service import archive
from .storage import list_runs, lookup

bp = Blueprint("runs", __name__)


@bp.post("/api/runs")
def post():
    snapshot, inserted = archive(current_app.config["DATABASE"], read_sources())
    return {"run_id": snapshot["run_id"], "created": inserted, "snapshot": snapshot}, 201 if inserted else 200


@bp.get("/api/runs")
def history():
    reports = list_runs(current_app.config["DATABASE"])
    return {"runs": [{k: record[k] for k in ("run_id", "rule", "created_at", "duration_ms")} for record in reports]}


@bp.get("/api/runs/<run_id>")
def detail(run_id):
    return lookup(current_app.config["DATABASE"], run_id)
