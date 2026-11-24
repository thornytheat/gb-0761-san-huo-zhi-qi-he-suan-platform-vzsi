from decimal import Decimal


def tier_costs(term, overtime):
    first = min(overtime, term["tier1_min"])
    for tier, duration in enumerate((first, overtime - first), 1):
        rate = Decimal(term[f"rate{tier}_usd_min"])
        yield {"tier": tier, "minutes": duration, "rate_usd_min": f"{rate:.2f}", "expected_usd": f"{rate * duration:.2f}"}
