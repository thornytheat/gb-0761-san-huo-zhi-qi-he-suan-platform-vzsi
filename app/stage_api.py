from .input import read_sources
from .pipeline import evaluate


def preview(stage):
    return evaluate(read_sources(), until=stage)[stage]
