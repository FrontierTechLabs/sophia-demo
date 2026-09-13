from typing import List, Dict, Any
from collections import Counter
from .constants import BENFORD_EXPECTED, BENFORD_EXPECTED_SECOND, MIN_NUMBERS_FOR_BENFORD

CAVEAT=("Benford's Law is designed for large, naturally-occurring transaction-level "
        "datasets. Numbers extracted from report narrative text (rounded summary "
        "figures, headline totals) are a weaker signal — treat this as informational "
        "screening, not forensic evidence of manipulation.")

def _band(v,lo,hi): return "LOW" if v<lo else ("MEDIUM" if v<hi else "HIGH")

def benford_analysis(numbers: List[float]) -> Dict[str, Any]:
    if not numbers:
        return {"status":"No numbers found","overall_risk":"INSUFFICIENT_DATA","caveat":CAVEAT}
    fd,sd=[],[]
    for n in numbers:
        if n>=1:
            s=str(int(abs(n))); fd.append(int(s[0]))
            if len(s)>=2: sd.append(int(s[1]))
    tf,ts=len(fd),len(sd)
    if tf<MIN_NUMBERS_FOR_BENFORD:
        return {"status":f"Insufficient data (found {tf}, need at least {MIN_NUMBERS_FOR_BENFORD})","overall_risk":"INSUFFICIENT_DATA","caveat":CAVEAT}
    fc=Counter(fd); fo={d:fc.get(d,0)/tf for d in range(1,10)}; fe={d:BENFORD_EXPECTED[d]/100 for d in range(1,10)}
    mad=sum(abs(fo[d]-fe[d]) for d in range(1,10))/9
    co=ce=ks=0.0
    for d in range(1,10):
        co+=fo[d]; ce+=fe[d]; ks=max(ks,abs(co-ce))
    chi=sum(((fc.get(d,0)-tf*fe[d])**2)/(tf*fe[d]) for d in range(1,10))
    mr=_band(mad,0.004,0.008); kr=_band(ks,0.02,0.04); cr="NOT COMPUTED (scipy not installed on demo)"
    if ts>=MIN_NUMBERS_FOR_BENFORD:
        sc=Counter(sd); so={d:sc.get(d,0)/ts for d in range(10)}; se={d:BENFORD_EXPECTED_SECOND[d]/100 for d in range(10)}
        mad2=sum(abs(so[d]-se[d]) for d in range(10))/10; mr2=_band(mad2,0.004,0.008)
    else: mad2,mr2=0.0,"INSUFFICIENT_DATA"
    rs={"LOW":0,"MEDIUM":1,"HIGH":2,"INSUFFICIENT_DATA":0,"NOT COMPUTED (scipy not installed on demo)":0}
    tot=rs.get(mr,0)+rs.get(kr,0)+rs.get(cr,0)+rs.get(mr2,0)
    overall="LOW" if tot<=1 else ("MEDIUM" if tot<=3 else "HIGH")
    return {"status":"Benford's Law applied","caveat":CAVEAT,"total_first_digits":tf,"total_second_digits":ts,
            "mad_first":mad,"mad_first_risk":mr,"ks_first":ks,"ks_first_risk":kr,
            "chi2_first":chi,"p_value":None,"chi_first_risk":cr,
            "mad_second":mad2,"mad_second_risk":mr2,"overall_risk":overall}
