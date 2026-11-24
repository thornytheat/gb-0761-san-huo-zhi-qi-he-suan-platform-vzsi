from flask import Blueprint

from app.stage_api import preview

bp = Blueprint("ledger", __name__)


@bp.post("/api/ledger")
def compute():
    return preview("ledger")
