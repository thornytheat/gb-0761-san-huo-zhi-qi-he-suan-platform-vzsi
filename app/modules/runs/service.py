from time import perf_counter

from app.manifest import snapshot
from app.pipeline import evaluate
from .storage import commit


def archive(db_path, sources):
    started = perf_counter()
    calculation = evaluate(sources)
    return commit(db_path, snapshot(sources, calculation, started))
