from flask import Blueprint

from app.stage_api import preview

bp = Blueprint("notice", __name__)


@bp.post("/api/notice")
def compute():
    return preview("notice")
