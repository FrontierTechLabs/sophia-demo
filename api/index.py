import os, io, sys, hmac, hashlib, base64, logging
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, Request, Response, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from .sophia.engine import forensic_scan_text
from .sophia.extract import extract_pdf_text
from .sophia.legal import LEGAL_REFERENCES
from .sophia.brand import logo_svg, page_shell, BASE_CSS

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
log = logging.getLogger("sophia")

PASSWORD = os.environ.get("SOPHIA_PASSWORD", "sophia-demo")
SECRET = os.environ.get("SOPHIA_SECRET", "sophia-default-secret-change-me")
COOKIE = "sophia_auth"

def _token(): return hmac.new(SECRET.encode(), b"sophia-authed-v1", hashlib.sha256).hexdigest()
def _authed(req: Request) -> bool:
    t = req.cookies.get(COOKIE)
    return bool(t) and hmac.compare_digest(t, _token())

app = FastAPI(title="Sophia Justice Agent v4.0")

def _logo_data_uri() -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(logo_svg().encode()).decode()

def _login_html(err: str = "") -> str:
    body = f"""
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px">
  <form method="POST" action="/login" style="background:linear-gradient(180deg,#111 0%,#0a0a0a 100%);border:1px solid #2a2318;border-radius:16px;padding:40px 32px;max-width:420px;width:100%;box-shadow:0 0 60px rgba(232,217,168,0.05)">
    <div style="text-align:center;margin-bottom:24px">{logo_svg().replace('<svg','<svg style="width:64px;height:64px"')}</div>
    <h1 style="text-align:center;font-size:22px;letter-spacing:.02em;color:#f0e2b0;margin-bottom:6px">Sophia Justice Agent</h1>
    <div style="text-align:center;font-size:12px;color:#8a7d5c;margin-bottom:28px;letter-spacing:.14em;text-transform:uppercase">Forensic Screening v4.0</div>
    <input type="password" name="password" placeholder="Access code" autofocus required>
    <button type="submit" style="width:100%;margin-top:16px">Enter</button>
    {f'<div class="err">{err}</div>' if err else ''}
  </form>
</div>"""
    return page_shell("Sophia — Access", body)

DASHBOARD_BODY = """
<div class="wrap">
<header>
  <div class="brand">__LOGO__<div><h1>Sophia Justice Agent v4.0</h1><div class="sub">Forensic Screening · Live Demo</div></div></div>
  <a class="logout" href="/logout">Sign out</a>
</header>

<div class="panel">
  <h2>1 · Submit Document</h2>
  <div class="drop" id="drop">
    <div class="big">Drop a PDF here</div>
    <p>or click to browse · annual reports · financial statements · title deeds</p>
    <input type="file" id="file" accept="application/pdf">
    <div id="fname" style="margin-top:10px;color:#c9a961;font-size:13px"></div>
  </div>
  <p style="font-size:11px;color:#8a7d5c;margin:20px 0 10px;letter-spacing:.14em;text-transform:uppercase">or paste text directly</p>
  <textarea id="pasted" placeholder="Paste report text here…"></textarea>
  <div class="row">
    <button id="scan">Run Forensic Scan</button>
    <button class="ghost" id="sample">Load Suspicious Sample</button>
    <button class="ghost" id="clear">Clear</button>
  </div>
  <div class="loading" id="loading">Analyzing document… running Benford, red-flag, entity, title-search passes…</div>
</div>
<div id="results"></div>
<div class="disc">
  <strong>Honest capability statement.</strong> This is an automated <em>screening</em> aid. Keyword/regex/statistical analysis of document text producing a law-referenced report to guide human review. It does not guarantee zero false positives, does not constitute a legal opinion, and does not cryptographically sign its output (this demo generates a SHA-512 integrity hash, not a signature). OCR is unavailable on this deployment — scanned PDFs without a text layer return a clear extraction error rather than a false "no red flags."
</div>
</div>
<script>
const drop=document.getElementById('drop'),file=document.getElementById('file'),fname=document.getElementById('fname'),
pasted=document.getElementById('pasted'),scan=document.getElementById('scan'),loading=document.getElementById('loading'),
results=document.getElementById('results');
let sel=null;
drop.addEventListener('click',()=>file.click());
drop.addEventListener('dragover',e=>{e.preventDefault();drop.classList.add('over');});
drop.addEventListener('dragleave',()=>drop.classList.remove('over'));
drop.addEventListener('drop',e=>{e.preventDefault();drop.classList.remove('over');if(e.dataTransfer.files.length){file.files=e.dataTransfer.files;pick();}});
file.addEventListener('change',pick);
function pick(){if(file.files.length){sel=file.files[0];fname.textContent='✓ '+sel.name+'  ('+(sel.size/1024).toFixed(0)+' KB)';}}
document.getElementById('sample').addEventListener('click',()=>{pasted.value=SAMPLE;sel=null;file.value='';fname.textContent='';});
document.getElementById('clear').addEventListener('click',()=>{pasted.value='';sel=null;file.value='';fname.textContent='';results.innerHTML='';});
scan.addEventListener('click',async()=>{
  const fd=new FormData();
  if(sel)fd.append('pdf',sel); else if(pasted.value.trim())fd.append('text',pasted.value);
  else{alert('Upload a PDF or paste text first.');return;}
  scan.disabled=true;loading.classList.add('on');results.innerHTML='';
  try{
    const r=await fetch('/scan',{method:'POST',body:fd});
    const d=await r.json();
    if(d.error){results.innerHTML='<div class="panel"><h2>Error</h2><pre>'+esc(d.error+'\\n'+(d.detail||''))+'</pre></div>';}
    else render(d);
  }catch(e){results.innerHTML='<div class="panel"><h2>Error</h2><pre>'+esc(String(e))+'</pre></div>';}
  finally{scan.disabled=false;loading.classList.remove('on');}
});
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function render(d){
  const v=d.verdict.replace(' RISK','');const pct=d.suspicion_score;
  const c=v==='HIGH'?'#e07a5f':v==='MEDIUM'?'#e0b34a':'#7bc47b';
  let h='<div class="panel"><h2>2 · Board Summary</h2><div class="score">';
  h+='<div class="dial" style="--c:'+c+';--p:'+pct+'%"><span>'+pct+'</span></div>';
  h+='<div><div class="verdict '+v+'">'+esc(d.verdict)+'</div>';
  h+='<div style="font-size:12px;color:#8a7d5c;margin-top:6px">Score '+pct+'/100 · '+d.statistics.flagged_categories+' flagged categor'+(d.statistics.flagged_categories===1?'y':'ies')+'</div>';
  if(d.score_caveats&&d.score_caveats.length)h+='<div style="font-size:12px;color:#e07a5f;margin-top:8px">⚠ '+esc(d.score_caveats.join(' '))+'</div>';
  h+='</div></div><div class="grid">';
  const stats=[['Characters',d.statistics.total_characters.toLocaleString()],['Financial numbers',d.statistics.financial_numbers.toLocaleString()],['Tables',d.statistics.tables_found],['Flagged categories',d.statistics.flagged_categories],['Named persons',d.statistics.named_persons_found],['Dates',d.chronology.length]];
  for(const[k,val]of stats)h+='<div class="stat"><div class="k">'+k+'</div><div class="v">'+val+'</div></div>';
  h+='</div><div class="row" style="margin-top:18px"><a href="/report/html" onclick="return openReport()" class="logout" style="padding:12px 22px;font-weight:700;letter-spacing:.1em">Download Branded Report (HTML)</a></div></div>';
  if(d.red_flags.length){
    h+='<div class="panel"><h2>3 · Financial &amp; Regulatory Findings</h2>';
    for(const f of d.red_flags){
      const cls=f.confidence==='HIGH'?'high':f.confidence==='MEDIUM'?'medium':'';
      h+='<div class="flag '+cls+'"><h3>'+esc(f.id.replace(/_/g,' '))+'</h3>';
      h+='<div class="conf">Confidence '+f.confidence+' · '+f.occurrence_count+' occurrence(s)</div>';
      for(const ev of f.evidence.slice(0,3))h+='<p>…'+esc(ev.context.slice(0,200))+'…</p>';
      if(f.occurrence_count>3)h+='<p style="color:#8a7d5c;font-size:12px">… and '+(f.occurrence_count-3)+' more in JSON</p>';
      if(f.legal_refs)for(const l of f.legal_refs)h+='<div class="law">⚖ '+esc(l)+'</div>';
      if(f.action)h+='<div class="action">→ '+esc(f.action)+'</div>';
      h+='</div>';
    }
    h+='</div>';
  }
  if(d.title_search){const t=d.title_search;h+='<div class="panel"><h2>4 · Title Search Analysis</h2>';
    if(t.confidence==='UNRECOGNIZED_FORMAT')h+='<p style="color:#e07a5f;font-size:13px">Format not recognized — manual review required.</p>';
    else h+='<pre>'+esc(JSON.stringify({property:t.property,first_party:t.parties.first_party,second_party:t.parties.second_party,registration:t.registration,legal_opinion:t.legal_opinion,confidence:t.confidence,red_flags:t.red_flags},null,2))+'</pre>';
    h+='</div>';}
  h+='<div class="panel"><h2>5 · Benford\'s Law</h2><pre>'+esc(JSON.stringify(d.benford_law,null,2))+'</pre></div>';
  h+='<div class="panel"><h2>6 · Entities</h2><pre>'+esc(JSON.stringify(d.entities,null,2))+'</pre></div>';
  if(d.chronology.length)h+='<div class="panel"><h2>7 · Chronology</h2><pre>'+esc(d.chronology.join('\\n'))+'</pre></div>';
  h+='<div class="panel"><h2>Integrity</h2><pre>'+esc(JSON.stringify(d.integrity,null,2))+'</pre></div>';
  h+='<div class="panel"><h2>Full JSON</h2><pre style="max-height:400px;overflow:auto">'+esc(JSON.stringify(d,null,2))+'</pre></div>';
  results.innerHTML=h;window.__lastReport=d;
}
function openReport(){if(!window.__lastReport){alert('Run a scan first.');return false;}
  fetch('/report/html',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(window.__lastReport)})
    .then(r=>r.text()).then(html=>{const w=window.open('','_blank');w.document.write(html);w.document.close();});
  return false;}
const SAMPLE=`BHARAT HOSPITALITY HOLDINGS LIMITED
Annual Report 2024-25 — Extracts

Independent Auditor's Report
We draw attention to Note 27 to the financial statements. The Company has incurred a net loss
of Rs. 42.7 Crore for the year ended 31 March 2025 and, as of that date, the Company's current
liabilities exceeded its current assets by Rs. 118.3 Crore. These conditions indicate the existence
of a material uncertainty that may cast significant doubt about the Company's ability to continue
as a going concern.

Note 27 — Going Concern
The Company's accumulated losses have eroded 62% of its paid-up capital. The Company has defaulted
on repayment of Rs. 18.5 Crore term loan instalment due on 15 January 2025.

Note 34 — Related Party Transactions
During the year, the Company entered into related party transactions with Sunrise Estates Private
Limited (a wholly owned subsidiary of the promoter group) amounting to Rs. 24.3 Crore towards
purchase of land where no independent valuation was obtained.

Note 41 — Contingent Liabilities
(i) Income Tax Department has issued a show cause notice (SCN) dated 12 February 2025 for alleged
under-reporting of income of Rs. 9.1 Crore.
(ii) Enforcement Directorate has initiated an investigation. Summons have been issued to two directors.
(iii) Pending litigation before the Delhi High Court in respect of a disputed property at Khasra No.
452/3, Village Kapashera. Arbitration proceedings are ongoing.
(iv) The Company has given corporate guarantees of Rs. 67.4 Crore for loans availed by a related entity.

Note 52 — Regulatory
The Reserve Bank of India has placed the Company's banking subsidiary under scrutiny following
NPA classification of Rs. 132 Crore of its loan book. SEBI has sought clarification.

Statutory Auditors: Mehta & Associates, Chartered Accountants (FRN 004512N)

FIRST PARTY: Sunrise Estates Private Limited
SECOND PARTY: Mr. Rajesh Mehta and Mrs. Kavita Mehta
PROPERTY ADDRESS: Khasra No. 452/3, Village Kapashera, New Delhi
DOC. REG NO. 4521/2019
ADDL. BOOK NO. 1
VOL NO. 4521
PAGE NOS. 112-118
REGD. DATE 12/08/2019
LEGAL OPINION: The title appears clear, however a caveat has been registered by a third party in
2021 which is sub-judice. This opinion is based on the basis of documents made available and we
assume no personal responsibility.
LIMITATION: This opinion does not cover encumbrances not appearing in the records of the Sub-Registrar.`;"""

DASHBOARD_HTML = page_shell("Sophia — Forensic Screening Demo", DASHBOARD_BODY.replace("__LOGO__", logo_svg().replace('<svg','<svg style="width:44px;height:44px"')))

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return HTMLResponse(DASHBOARD_HTML if _authed(request) else _login_html())

@app.post("/login")
async def login(password: str = Form(...)):
    if hmac.compare_digest(password, PASSWORD):
        r = RedirectResponse(url="/", status_code=303)
        r.set_cookie(COOKIE, _token(), httponly=True, secure=True, samesite="lax", max_age=60*60*12)
        return r
    return HTMLResponse(_login_html("Incorrect access code."), status_code=401)

@app.get("/logout")
async def logout():
    r = RedirectResponse(url="/", status_code=303); r.delete_cookie(COOKIE); return r

@app.post("/scan")
async def scan_endpoint(request: Request, pdf: Optional[UploadFile]=File(None), text: Optional[str]=Form(None)):
    if not _authed(request): raise HTTPException(status_code=401, detail="Not authenticated")
    if pdf is not None:
        b = await pdf.read()
        if not b: return JSONResponse({"error":"Empty PDF upload."}, status_code=400)
        extracted, method = extract_pdf_text(b)
        if not extracted.strip():
            return JSONResponse({"error":"Could not extract text from this PDF.",
                                 "detail":method+" — if this is a scanned document, OCR is not available. Please paste the text directly instead."}, status_code=422)
        return JSONResponse(forensic_scan_text(extracted, f"{pdf.filename or 'uploaded.pdf'} (via {method})", pdf_bytes=b))
    if text and text.strip(): return JSONResponse(forensic_scan_text(text, "pasted text"))
    return JSONResponse({"error":"Provide a PDF file or pasted text."}, status_code=400)

@app.post("/report/html", response_class=HTMLResponse)
async def report_html(request: Request):
    if not _authed(request): raise HTTPException(status_code=401)
    d = await request.json()
    body = _render_report_page(d)
    return HTMLResponse(body)

def _render_report_page(d: dict) -> str:
    v = d["verdict"].replace(" RISK","")
    pct = d["suspicion_score"]
    color = "#e07a5f" if v=="HIGH" else "#e0b34a" if v=="MEDIUM" else "#7bc47b"
    def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    flags_html = ""
    for f in d.get("red_flags",[]):
        ref = LEGAL_REFERENCES.get(f["id"],{})
        cls = "high" if f["confidence"]=="HIGH" else "medium" if f["confidence"]=="MEDIUM" else ""
        flags_html += f'<div class="flag {cls}"><h3>{esc(f["id"].replace("_"," "))}</h3>'
        flags_html += f'<div class="conf">Confidence {f["confidence"]} · {f["occurrence_count"]} occurrence(s)</div>'
        if ref.get("summary"): flags_html += f'<p><em>{esc(ref["summary"])}</em></p>'
        for ev in f["evidence"][:3]:
            flags_html += f'<p>…{esc(ev["context"][:220])}…</p>'
        if ref.get("laws"):
            for law in ref["laws"][:4]: flags_html += f'<div class="law">⚖ {esc(law)}</div>'
        if ref.get("action"): flags_html += f'<div class="action">→ {esc(ref["action"])}</div>'
        flags_html += '</div>'
    title_html = ""
    t = d.get("title_search")
    if t:
        if t.get("confidence")=="UNRECOGNIZED_FORMAT":
            title_html = '<p style="color:#e07a5f">Format not recognized by parser — manual review required. This is a parser limitation, not a finding.</p>'
        else:
            title_html = f"""<pre>Property: {esc(t.get('property') or '—')}
First Party: {esc(', '.join(t['parties']['first_party']) or '—')}
Second Party: {esc(', '.join(t['parties']['second_party']) or '—')}
Registration: {esc(t.get('registration') or {})}
Legal Opinion: {esc(t.get('legal_opinion') or '—')}
Extraction Confidence: {esc(t.get('confidence'))}
Red Flags: {esc('; '.join(t.get('red_flags') or []) or 'none')}</pre>"""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Sophia Forensic Report — {esc(d['document'])}</title>
<style>
body{{font-family:ui-sans-serif,system-ui,sans-serif;background:#fff;color:#1a1a1a;max-width:900px;margin:0 auto;padding:40px 30px;line-height:1.55}}
.rpt-head{{display:flex;align-items:center;gap:18px;border-bottom:3px solid #c9a961;padding-bottom:20px;margin-bottom:30px}}
.rpt-head svg{{width:64px;height:64px}}
h1{{font-size:22px;margin:0;color:#1a1a1a;letter-spacing:.02em}}
.rpt-sub{{font-size:12px;color:#8a7d5c;letter-spacing:.14em;text-transform:uppercase;margin-top:4px}}
h2{{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:#8a6d2f;border-bottom:1px solid #e0d5b0;padding-bottom:8px;margin:32px 0 16px}}
.score-row{{display:flex;align-items:center;gap:24px;margin:20px 0}}
.dial{{width:110px;height:110px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:700;background:conic-gradient({color} {pct}%,#eee 0);position:relative;color:#1a1a1a}}
.dial::before{{content:"";position:absolute;inset:10px;border-radius:50%;background:#fff}}
.dial span{{position:relative;z-index:2}}
.verdict{{font-size:24px;font-weight:700;color:{color}}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:16px 0}}
.stat{{border:1px solid #e0d5b0;border-radius:8px;padding:12px}}
.stat .k{{font-size:10px;color:#8a7d5c;letter-spacing:.1em;text-transform:uppercase}}
.stat .v{{font-size:18px;font-weight:600;color:#1a1a1a;margin-top:4px}}
.flag{{border-left:3px solid #c9a961;padding:14px 18px;margin-bottom:14px;background:#faf8f0;border-radius:0 8px 8px 0}}
.flag.high{{border-left-color:#c94f2f}}.flag.medium{{border-left-color:#c9a961}}
.flag h3{{font-size:14px;margin:0 0 6px;text-transform:capitalize;color:#1a1a1a}}
.flag .conf{{font-size:11px;color:#8a7d5c;letter-spacing:.06em;text-transform:uppercase;margin-bottom:10px}}
.flag p{{font-size:13px;margin:6px 0;color:#333}}
.flag .law{{font-size:12px;color:#6a5a30;padding-left:12px;border-left:1px solid #c9a961;margin:4px 0;line-height:1.5}}
.flag .action{{font-size:12px;color:#8a6d2f;margin-top:10px;font-style:italic}}
pre{{background:#faf8f0;border:1px solid #e0d5b0;border-radius:8px;padding:14px;font-size:12px;overflow-x:auto;white-space:pre-wrap;word-break:break-word}}
.disc{{font-size:12px;color:#8a7d5c;line-height:1.7;padding:16px;background:#faf8f0;border:1px solid #e0d5b0;border-radius:8px;margin-top:24px}}
.hash{{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#666;word-break:break-all}}
.print-btn{{position:fixed;bottom:24px;right:24px;padding:14px 22px;background:#c9a961;color:#fff;border:none;border-radius:10px;font-size:13px;font-weight:700;letter-spacing:.1em;cursor:pointer;text-transform:uppercase;box-shadow:0 4px 20px rgba(0,0,0,.15)}}
@media print{{.print-btn{{display:none}} body{{padding:0}}}}
</style></head><body>
<div class="rpt-head">{logo_svg().replace('<svg','<svg style="width:64px;height:64px"')}<div><h1>Sophia Forensic Screening Report</h1><div class="rpt-sub">Sovereign Intelligence Mesh · Satya Universe</div></div></div>
<p style="font-size:13px;color:#666">Document: <strong>{esc(d['document'])}</strong><br>Generated: {esc(d['analysis_date'])}</p>
<div class="score-row"><div class="dial"><span>{pct}</span></div><div><div class="verdict">{esc(d['verdict'])}</div><div style="font-size:13px;color:#666">Suspicion score {pct}/100</div>{('<div style="font-size:12px;color:#c94f2f;margin-top:6px">⚠ '+esc(' '.join(d.get('score_caveats',[])))+'</div>') if d.get('score_caveats') else ''}</div></div>
<h2>Statistics</h2>
<div class="grid">{''.join(f'<div class="stat"><div class="k">{k}</div><div class="v">{v}</div></div>' for k,v in [('Characters',d['statistics']['total_characters']),('Financial numbers',d['statistics']['financial_numbers']),('Tables found',d['statistics']['tables_found']),('Flagged categories',d['statistics']['flagged_categories']),('Named persons',d['statistics']['named_persons_found']),('Dates',len(d['chronology']))])}</div>
<h2>Financial &amp; Regulatory Findings</h2>
{flags_html or '<p style="color:#666">No red flags detected in this pass.</p>'}
{('<h2>Title Search Analysis</h2>'+title_html) if t else ''}
<h2>Benford's Law — Statistical Screening</h2>
<pre>{esc(d['benford_law'].get('status',''))}\n{esc(d['benford_law'].get('caveat',''))}\nMAD First: {d['benford_law'].get('mad_first',0):.4f} ({d['benford_law'].get('mad_first_risk','')})\nMAD Second: {d['benford_law'].get('mad_second',0):.4f} ({d['benford_law'].get('mad_second_risk','')})\nOverall: {esc(d['benford_law'].get('overall_risk',''))}</pre>
<h2>Entities Extracted</h2>
<pre>{esc(str(d['entities']))}</pre>
{('<h2>Chronology</h2><pre>'+esc(chr(10).join(d['chronology']))+'</pre>') if d['chronology'] else ''}
<h2>Integrity Record</h2>
<p style="font-size:12px">Type: <strong>{esc(d['integrity']['type'])}</strong></p>
<p class="hash">SHA-512: {esc(d['integrity']['content_hash_sha512'])}</p>
<div class="disc"><strong>Honest capability statement.</strong> This is an automated screening aid — not a legal opinion, not a forensic audit finding, not a guarantee of zero false positives. Every score and verdict is a prioritization aid to guide human review, not a conclusion. This report was generated by Sophia Justice Agent v4.0 and carries a SHA-512 integrity hash of its body. The hash detects post-generation tampering only if independently recomputed; it does not prove authorship.</div>
<button class="print-btn" onclick="window.print()">Print / Save as PDF</button>
</body></html>"""

@app.get("/health")
async def health():
    return {"status":"ok","engine":"sophia-forensic-v4"}

# ── Vercel entrypoint ──
