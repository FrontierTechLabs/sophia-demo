from .legal import LEGAL_REFERENCES

def generate_board_summary(flags, benford, score, verdict, score_caveats, title_findings, integrity) -> str:
    L=[]
    L.append("="*80); L.append("BOARD SUMMARY — SOPHIA FORENSIC SCREENING REPORT"); L.append("="*80); L.append("")
    L.append("Automated SCREENING aid, not a legal or forensic-accounting finding.")
    L.append("All items require human review before any conclusion is drawn."); L.append("")
    L.append(f"Suspicion Score: {score}/100 — {verdict}")
    for c in score_caveats: L.append(f"   ! {c}")
    L.append("")
    if flags:
        L.append(f"FINANCIAL / REGULATORY FINDINGS ({len(flags)} categories):")
        for f in flags:
            ref=LEGAL_REFERENCES.get(f["id"],{"summary":"","laws":[],"action":""})
            L.append(""); L.append(f"  * {ref['summary']}")
            L.append(f"    Confidence: {f['confidence']} | Occurrences: {f['occurrence_count']}")
            for i,ev in enumerate(f["evidence"][:3],1):
                L.append(f"    [{i}] ...{ev['context'][:140]}...")
            if f["occurrence_count"]>3: L.append(f"    ... and {f['occurrence_count']-3} more in JSON")
            L.append("    Legal References:")
            for law in ref["laws"][:4]: L.append(f"      - {law}")
            L.append(f"    Recommended Action: {ref['action']}")
    else:
        L.append("FINANCIAL / REGULATORY FINDINGS: None detected in this pass.")
        L.append("   (Absence of keyword match != absence of risk.)")
    if benford.get("status")=="Benford's Law applied":
        L.append(""); L.append("STATISTICAL ANALYSIS (Benford's Law) — INFORMATIONAL:")
        L.append(f"  * {benford['caveat']}")
        L.append(f"  * First Digit MAD: {benford['mad_first']:.4f} ({benford['mad_first_risk']})")
        L.append(f"  * Second Digit MAD: {benford['mad_second']:.4f} ({benford['mad_second_risk']})")
        L.append(f"  * Overall: {benford['overall_risk']}")
    else:
        L.append(""); L.append(f"Benford's Law: {benford.get('status','n/a')}")
    if title_findings:
        L.append(""); L.append("TITLE SEARCH ANALYSIS:")
        if title_findings["confidence"]=="UNRECOGNIZED_FORMAT":
            L.append("  ! Format not recognized — manual review required.")
        else:
            L.append(f"  * Property: {title_findings.get('property') or 'Not specified'}")
            L.append(f"  * First Party: {', '.join(title_findings['parties']['first_party'][:2]) or 'Not extracted'}")
            L.append(f"  * Second Party: {', '.join(title_findings['parties']['second_party'][:2]) or 'Not extracted'}")
            L.append(f"  * Registration: {title_findings['registration'] or 'Not extracted'}")
            L.append(f"  * Confidence: {title_findings['confidence']}")
            if title_findings.get("red_flags"):
                L.append("  * Title Red Flags:")
                for rf in title_findings["red_flags"]: L.append(f"      - {rf}")
    L.append(""); L.append("="*80)
    L.append("This report is a statistical and contextual screening aid — not a finding")
    L.append(f"of guilt, fraud, or defective title. Human review required.")
    L.append(f"Report integrity: {integrity['type']}."); L.append("="*80)
    return "\n".join(L)
