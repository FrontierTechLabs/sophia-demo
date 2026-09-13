import io, re
from typing import Tuple, List
try: import pdfplumber; PDFPLUMBER_AVAILABLE=True
except ImportError: PDFPLUMBER_AVAILABLE=False
try: import PyPDF2; PYPDF2_AVAILABLE=True
except ImportError: PYPDF2_AVAILABLE=False
from .constants import FINANCIAL_KEYWORDS

def extract_pdf_text(pdf_bytes: bytes) -> Tuple[str, str]:
    attempts=[]
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text="".join((p.extract_text() or "")+"\n" for p in pdf.pages)
            if text.strip(): return text,"pdfplumber"
            attempts.append("pdfplumber: no text extracted (possibly scanned)")
        except Exception as e: attempts.append(f"pdfplumber failed: {e}")
    if PYPDF2_AVAILABLE:
        try:
            r=PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            if r.is_encrypted:
                try: r.decrypt("")
                except Exception: attempts.append("PyPDF2: PDF is password-protected")
            text="".join((p.extract_text() or "")+"\n" for p in r.pages)
            if text.strip(): return text,"PyPDF2"
            attempts.append("PyPDF2: no text extracted")
        except Exception as e: attempts.append(f"PyPDF2 failed: {e}")
    attempts.append("OCR unavailable on this deployment (Vercel serverless — no tesseract binary)")
    return ""," | ".join(attempts)

def extract_tables(pdf_bytes: bytes) -> List:
    if not PDFPLUMBER_AVAILABLE: return []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            out=[]
            for p in pdf.pages:
                t=p.extract_tables()
                if t: out.extend(t)
            return out
    except Exception: return []

def extract_financial_numbers(text: str) -> List[float]:
    nums=[]; np=re.compile(r"-?\d{1,3}(?:,\d{3})*(?:\.\d+)?")
    units=("₹","Rs.","Rs ","Rupees","Lakh","Crore","Million","Billion")
    for line in text.split("\n"):
        if len(line.strip())<3: continue
        if not any(k in line for k in FINANCIAL_KEYWORDS): continue
        for m in np.finditer(line):
            try: n=float(m.group(0).replace(",",""))
            except ValueError: continue
            if not (0<abs(n)<1e15): continue
            ctx=line[max(0,m.start()-40):min(len(line),m.end()+40)]
            if any(u in ctx for u in units): nums.append(n)
    return nums
