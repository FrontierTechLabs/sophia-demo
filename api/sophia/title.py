import re
from typing import Dict, Any

def analyze_title_search(text: str) -> Dict[str, Any]:
    r={"report_type":"Title Search Report","parties":{"first_party":[],"second_party":[]},"property":"",
       "registration":{},"legal_opinion":"","limitations":[],"red_flags":[],"data_quality_notes":[],"confidence":"LOW"}
    fp={"first_party":[r"FIRST PARTY\s*[:\-]\s*(.*?)(?=SECOND PARTY|DOC\.?\s*REG|$)"],
        "second_party":[r"SECOND PARTY\s*[:\-]\s*(.*?)(?=DOC\.?\s*REG|REGD\.?\s*DATE|I have duly|$)"],
        "property":[r"PROPERTY ADDRESS\s*[:\-]\s*(.*?)(?=DOC\.?\s*REG|REGD\.?\s*DATE|I have duly|$)",
                    r"SCHEDULE OF PROPERTY\s*[:\-]\s*(.*?)(?=DOC\.?\s*REG|REGD\.?\s*DATE|WITNESS|$)"]}
    for f,pats in fp.items():
        for p in pats:
            m=re.search(p,text,re.DOTALL|re.I)
            if m and m.group(1).strip():
                v=m.group(1).strip()
                if f=="property": r["property"]=v
                else: r["parties"][f]=[l.strip() for l in v.split("\n") if l.strip()]
                break
    if not r["property"]:
        k=re.search(r"KHASRA NO\.?\s*([\d/.]+)",text,re.I); s=re.search(r"SURVEY (?:NO|NUMBER)\.?\s*([\d/.]+)",text,re.I)
        if k: r["property"]=f"Khasra No. {k.group(1)}"
        elif s: r["property"]=f"Survey No. {s.group(1)}"
    for key,p in {"doc_reg_no":r"DOC\.?\s*REG\s*NO\.?\s*([\d/]+)","addl_book_no":r"ADDL\.?\s*BOOK\s*NO\.?\s*([\w\d]+)",
                  "volume_no":r"VOL(?:UME)?\.?\s*NO\.?\s*([\w\d]+)","pages":r"PAGE\s*NOS?\.?\s*([\d\-\s]+)",
                  "reg_date":r"REG(?:D|ISTRATION)?\.?\s*DATE\s*[:\-]?\s*([\d./\-]+)"}.items():
        m=re.search(p,text,re.I)
        if m: r["registration"][key]=m.group(1).strip()
    om=re.search(r"LEGAL OPINION\s*[:\-]\s*(.*?)(?=LIMITATION|DISCLAIMER|\n\s*\n|$)",text,re.DOTALL|re.I)
    if om: r["legal_opinion"]=om.group(1).strip()
    r["limitations"]=[l.strip() for l in re.findall(r"(?i)(?:limitation|disclaimer|does not cover|not responsible|no personal responsibility).{0,200}",text)][:5]
    c=sum([bool(r["parties"]["first_party"]),bool(r["parties"]["second_party"]),bool(r["property"]),bool(r["registration"]),bool(r["legal_opinion"])])
    if c==0:
        r["data_quality_notes"].append("Document format not recognized. PARSER LIMITATION, not a finding.")
        r["confidence"]="UNRECOGNIZED_FORMAT"
    else:
        r["confidence"]="LOW" if c<=2 else ("MEDIUM" if c<=4 else "HIGH")
        if c>=2:
            if not r["parties"]["first_party"] or not r["parties"]["second_party"]: r["red_flags"].append("One or both parties not identified")
            if not r["property"]: r["red_flags"].append("Property description missing or incomplete")
            if not r["registration"]: r["red_flags"].append("Registration details missing")
    tl=text.lower()
    if "caveat" in tl: r["red_flags"].append("Caveat present — recorded objection or claim on the property")
    if "sub-judice" in tl or "sub judice" in tl: r["red_flags"].append("Property described as sub-judice — active litigation")
    if "not verified" in tl or "on the basis of documents made available" in tl:
        r["red_flags"].append("Opinion limited to client-provided documents — not independently verified")
    return r
