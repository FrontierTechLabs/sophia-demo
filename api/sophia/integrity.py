import json, hashlib
from datetime import datetime, timezone
from typing import Dict, Any

def generate_integrity_record(report_body: Dict[str, Any]) -> Dict[str, Any]:
    canonical=json.dumps(report_body,sort_keys=True,default=str).encode("utf-8")
    return {"content_hash_sha512":hashlib.sha512(canonical).hexdigest(),
            "hash_covers":"the full report body (findings, scores, entities, chronology)",
            "generated_at":datetime.now(timezone.utc).isoformat(),
            "type":"SHA-512 integrity hash (not a cryptographic signature)",
            "note":"This hash proves the report content matches what was hashed if you recompute it yourself — it does NOT prove who generated it.",
            "verifiable":False}
