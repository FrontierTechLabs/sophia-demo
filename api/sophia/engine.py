import re, json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .extract import extract_pdf_text, extract_tables, extract_financial_numbers
from .benford import benford_analysis
from .entities import extract_entities
from .redflags import detect_red_flags
from .title import analyze_title_search
from .score import compute_suspicion_score, extract_chronology
from .integrity import generate_integrity_record
from .report import generate_board_summary

def forensic_scan_text(text: str, source_label: str, pdf_bytes: Optional[bytes]=None) -> Dict[str, Any]:
    if not text.strip():
        return {"error":"Could not extract any text from this document.","detail":source_label}
    title=None
    if re.search(r"(?:title search|legal opinion|sale deed|khasra no\.|registration act)",text,re.I):
        title=analyze_title_search(text)
    tables=extract_tables(pdf_bytes) if pdf_bytes else []
    nums=extract_financial_numbers(text)
    np=re.compile(r"-?\d{1,3}(?:,\d{3})*(?:\.\d+)?")
    for t in tables:
        for row in t:
            for cell in row:
                if cell and isinstance(cell,str):
                    for m in np.finditer(cell):
                        try:
                            n=float(m.group(0).replace(",",""))
                            if 0<abs(n)<1e15: nums.append(n)
                        except ValueError: pass
    benford=benford_analysis(nums)
    entities=extract_entities(text)
    flags=detect_red_flags(text)
    chrono=extract_chronology(text)
    score,cav=compute_suspicion_score(flags,benford.get("overall_risk","LOW"),len(text))
    if title and title["confidence"]!="UNRECOGNIZED_FORMAT":
        score=min(100,score+len(title.get("red_flags",[]))*3)
    verdict="HIGH RISK" if score>=50 else ("MEDIUM RISK" if score>=25 else "LOW RISK")
    body={"document":source_label,"analysis_date":datetime.now(timezone.utc).isoformat(),
          "extraction_method":source_label,"suspicion_score":score,"score_caveats":cav,"verdict":verdict,
          "statistics":{"total_characters":len(text),"financial_numbers":len(nums),"tables_found":len(tables),
                        "flagged_categories":len(flags),"named_persons_found":len(entities["named_persons"]),
                        "subsidiaries_found":len(entities["subsidiaries"])},
          "benford_law":benford,"entities":entities,"red_flags":flags,"chronology":chrono,"title_search":title}
    integ=generate_integrity_record(body)
    body["integrity"]=integ
    body["board_summary"]=generate_board_summary(flags,benford,score,verdict,cav,title,integ)
    return body
