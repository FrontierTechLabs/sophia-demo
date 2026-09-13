import re
from typing import List, Dict, Tuple

def compute_suspicion_score(flags: List[Dict], benford_risk: str, total_chars: int) -> Tuple[int, List[str]]:
    s=sum(f.get("weight",5) for f in flags)
    if benford_risk=="HIGH": s+=25
    elif benford_risk=="MEDIUM": s+=12
    c=[]
    if total_chars<1000:
        c.append("Very little text was extracted — score confidence is LOW regardless of the number shown.")
    return max(0,min(100,s)),c

def extract_chronology(text: str) -> List[str]:
    pats=[r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
          r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",r"\b\d{4}[-/]\d{2}[-/]\d{2}\b",
          r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b"]
    d=set()
    for p in pats: d.update(m.group(0) for m in re.finditer(p,text))
    return sorted(d)[:15]
