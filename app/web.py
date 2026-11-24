from datetime import datetime, timezone

from flask import Blueprint, abort, current_app, render_template, request

from .config import FILES, RULE
from .errors import Rejected
from .input import sample
from .modules.evidence.service import certify
from .modules.runs.service import archive
from .modules.runs.storage import list_runs, lookup
from .pipeline import evaluate
from .presentation import NAMES, panel

bp = Blueprint("web", __name__)


@bp.route("/", methods=["GET", "POST"])
@bp.route("/<stage>", methods=["GET", "POST"])
def view(stage="ledger"):
    if stage not in NAMES:
        abort(404)
    mode = request.values.get("sample", "dirty")
    saved, certificate, error, results = None, None, None, {}
    records, sources = [], {}
    database = current_app.config["DATABASE"]
    try:
        sources = ({key: request.form.get(key, "") for key in FILES}
                   if request.method == "POST" and mode == "custom" else sample(mode))
        if stage == "runs":
            if request.method == "POST":
                saved, inserted = archive(database, sources)
            records = list_runs(database)
        elif stage == "evidence":
            records = list_runs(database)
            run_id = request.args.get("run") or (records[0]["run_id"] if records else None)
            if run_id:
                certificate = certify(lookup(database, run_id))
        else:
            results = evaluate(sources, stage)
    except Rejected as exc:
        error = exc.code
    clock = results.get("clock", {})
    ledger = results.get("ledger", {})
    intake = results.get("intake", {})
    table = panel(stage, results[stage]) if stage in results and stage != "ledger" else None
    return render_template("desk.html", names=NAMES, stage=stage, mode=mode, sources=sources,
                           generated=datetime.now(timezone.utc).strftime("%m-%d %H:%M UTC"),
                           rule=RULE, error=error, clock=clock, ledger=ledger, intake=intake, table=table,
                           results=results, records=records, saved=saved, certificate=certificate,
                           inserted=inserted if saved else None)
