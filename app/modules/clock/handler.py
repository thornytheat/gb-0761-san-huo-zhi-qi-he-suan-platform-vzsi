from flask import Blueprint

from app.stage_api import preview

bp = Blueprint("clock", __name__)


@bp.post("/api/clock")
def compute():
    return preview("clock")
