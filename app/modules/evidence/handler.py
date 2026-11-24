from flask import Blueprint, current_app, jsonify

from app.modules.runs.storage import lookup
from .service import certify

bp = Blueprint("evidence", __name__)


@bp.get("/api/evidence/<run_id>")
def review(run_id):
    return certify(lookup(current_app.config["DATABASE"], run_id))


@bp.get("/api/export/<run_id>")
def download(run_id):
    response = jsonify(review(run_id))
    response.headers["Content-Disposition"] = f'attachment; filename="laytime-{run_id[:12]}.json"'
    return response
