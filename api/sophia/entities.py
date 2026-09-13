import re
from typing import Dict, List

BANKS_RE=r"\b(State Bank of India|Bank of Baroda|Bank of India|Punjab National Bank|ICICI Bank|HDFC Bank|Axis Bank|Kotak Mahindra Bank|Yes Bank|IndusInd Bank|Reserve Bank of India|IDBI Bank|Canara Bank|Union Bank|Federal Bank|PNB|ICICI|HDFC|RBI|SBI|IDBI)\b"

def extract_entities(text: str) -> Dict[str, List[str]]:
    e={"named_persons":[],"subsidiaries":[],"auditors":[],"banks":[]}
    for m in re.finditer(r"(?:Mr\.|Ms\.|Dr\.|Mrs\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})",text):
        n=m.group(1).strip()
        if 2<len(n)<60: e["named_persons"].append(m.group(0).strip())
    for m in re.finditer(r"(?:subsidiary|subsidiaries|wholly[- ]owned)\s*(?:of|:)?\s*([A-Z][a-zA-Z&,.\s]{2,60}?(?:Limited|Ltd\.?|Private Limited|Pvt\.? Ltd\.?))",text,re.I):
        e["subsidiaries"].append(m.group(1).strip())
    for m in re.finditer(r"(?:Statutory Auditors?|Independent Auditors?)\s*:?\s*([^\n.]{3,100})",text):
        e["auditors"].append(m.group(1).strip())
    for m in re.finditer(BANKS_RE,text): e["banks"].append(m.group(1))
    for k in e: e[k]=sorted(set(e[k]))[:20]
    return e
