import hashlib
import json


def certify(snapshot):
    payload = json.dumps(snapshot, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    evidence = snapshot["results"]
    return {"snapshot": snapshot, "integrity_sha256": hashlib.sha256(payload).hexdigest(),
            "can_settle": evidence["ledger"]["complete"] and not evidence["clock"]["missing"]
            and not evidence["ledger"]["differences"] and evidence["clock"]["balanced"],
            "evidence_counts": {"intervals": len(evidence["clock"]["rows"]), "tiers": len(evidence["ledger"]["rows"]),
                                "isolated": len(evidence["intake"]["isolated"])}}
