from decimal import Decimal

from .rates import tier_costs


def compare(notice, clock, invoice, quarantined):
    actuals = {item["tier"]: item for item in invoice}
    rows = []
    for tier in tier_costs(notice["term"], clock["overtime_min"]):
        actual = actuals.get(tier["tier"])
        disputed = [q["line"] for q in quarantined if q["source"] == "invoice" and q["code"] == "KEY_CONFLICT"
                    and q["key"] == tier["tier"]]
        if actual is None:
            code = "INVOICE_CONFLICT" if disputed else "INVOICE_MISSING"
            rows.append({**tier, "code": code, "invoice_line": None, "conflict_lines": disputed,
                         "actual_usd": None, "actual_minutes": None, "delta_usd": None})
            continue
        delta = Decimal(tier["expected_usd"]) - Decimal(actual["usd"])
        code = "MATCH" if not delta and tier["minutes"] == actual["minutes"] else "TIER_DIFFERENCE"
        rows.append({**tier, "code": code, "invoice_line": actual["line"], "actual_usd": actual["usd"],
                     "actual_minutes": actual["minutes"], "delta_usd": f"{delta:.2f}"})
    complete = all(r["delta_usd"] is not None for r in rows)
    expected = sum(Decimal(r["expected_usd"]) for r in rows)
    seen = sum(Decimal(r["actual_usd"]) for r in rows if r["actual_usd"] is not None)
    return {"expected_usd": f"{expected:.2f}", "seen_invoice_usd": f"{seen:.2f}",
            "delta_usd": f"{expected - seen:.2f}" if complete else None,
            "complete": complete, "differences": sum(r["code"] != "MATCH" for r in rows), "rows": rows}
