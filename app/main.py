import os

from flask import Flask

from .errors import Rejected
from .modules.clock.handler import bp as clock
from .modules.evidence.handler import bp as evidence
from .modules.exceptions.handler import bp as exceptions
from .modules.intake.handler import bp as intake
from .modules.ledger.handler import bp as ledger
from .modules.notice.handler import bp as notice
from .modules.runs.handler import bp as runs
from .web import bp as workbench


def create_app(database=None):
    app = Flask(__name__)
    app.config.update(DATABASE=database or os.environ.get("HARBOR_DB", "instance/ledger.sqlite"),
                      MAX_CONTENT_LENGTH=4_000_000)
    for blueprint in (intake, notice, exceptions, clock, ledger, runs, evidence, workbench):
        app.register_blueprint(blueprint)

    @app.errorhandler(Rejected)
    def handle(exc):
        return {"code": exc.code, "source": exc.source}, exc.status

    @app.get("/healthz")
    def health():
        return {"status": "ok"}

    return app
