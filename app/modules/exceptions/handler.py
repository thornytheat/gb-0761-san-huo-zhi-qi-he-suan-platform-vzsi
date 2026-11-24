from flask import Blueprint

from app.stage_api import preview

bp = Blueprint("exceptions", __name__)


@bp.post("/api/exceptions")
def compute():
    return preview("exceptions")
