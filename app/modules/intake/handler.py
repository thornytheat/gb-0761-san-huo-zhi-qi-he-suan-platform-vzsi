from flask import Blueprint

from app.stage_api import preview

bp = Blueprint("intake", __name__)


@bp.post("/api/intake")
def compute():
    return preview("intake")
