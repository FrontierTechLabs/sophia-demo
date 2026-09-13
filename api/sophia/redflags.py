import re
from typing import List, Dict, Any
from .patterns import RED_FLAG_PATTERNS
from .constants import MAX_EVIDENCE_PER_CATEGORY

def detect_red_flags(text: str) -> List[Dict[str, Any]]:
    flags=[]
    for fid,cfg in RED_FLAG_PATTERNS.items():
        occ=[]; seen=set()
        for pat,rflags in cfg["patterns"]:
            for m in re.finditer(pat,text,rflags):
                k=(m.start(),m.group(0))
                if k in seen: continue
                ctx=text[max(0,m.start()-100):min(len(text),m.end()+100)].replace("\n"," ").strip()
                if not any(kw in ctx.lower() for kw in cfg.get("context_keywords",[])): continue
                seen.add(k); occ.append({"match":m.group(0),"context":ctx})
                if len(occ)>=MAX_EVIDENCE_PER_CATEGORY: break
            if len(occ)>=MAX_EVIDENCE_PER_CATEGORY: break
        if occ:
            flags.append({"id":fid,"weight":cfg["weight"],"occurrence_count":len(occ),"evidence":occ,
                          "confidence":"HIGH" if cfg["weight"]>=15 else "MEDIUM" if cfg["weight"]>=10 else "LOW"})
    return flags
