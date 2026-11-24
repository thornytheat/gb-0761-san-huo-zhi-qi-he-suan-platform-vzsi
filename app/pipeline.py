from .modules.intake.service import accept
from .modules.notice.service import decide
from .modules.exceptions.service import slice_window
from .modules.clock.service import replay
from .modules.ledger.service import compare


STAGES = ("intake", "notice", "exceptions", "clock", "ledger")


def evaluate(sources, until="ledger"):
    result = {"intake": accept(sources)}
    if until == "intake":
        return result
    data = result["intake"]["accepted"]
    result["notice"] = decide(data["events"], data["terms"])
    if until == "notice":
        return result
    result["exceptions"] = slice_window(result["notice"], data["stops"])
    if until == "exceptions":
        return result
    result["clock"] = replay(result["notice"], result["exceptions"]["segments"])
    if until == "clock":
        return result
    result["ledger"] = compare(result["notice"], result["clock"], data["invoice"], result["intake"]["isolated"])
    return result
