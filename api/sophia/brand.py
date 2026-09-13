"""Brand assets: logo SVG, colour palette, page shell."""
from pathlib import Path

_GOLD = "#c9a961"
_GOLD_BRIGHT = "#f0d78c"
_BG = "#0a0a0a"
_INK = "#e8d9a8"
_MUTED = "#8a7d5c"

def logo_svg() -> str:
    try:
        return (Path(__file__).parent.parent / "static" / "logo.svg").read_text(encoding="utf-8")
    except Exception:
        return '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="46" fill="#0a0a0a" stroke="#c9a961"/><text x="50" y="62" text-anchor="middle" fill="#c9a961" font-size="40">S</text></svg>'

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0a0a;color:#e8d9a8;font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;min-height:100vh;line-height:1.5}
a{color:#c9a961;text-decoration:none}
.wrap{max-width:1100px;margin:0 auto;padding:24px}
header{display:flex;justify-content:space-between;align-items:center;padding:18px 0;border-bottom:1px solid #2a2318;margin-bottom:28px;flex-wrap:wrap;gap:12px}
.brand{display:flex;align-items:center;gap:14px}
.brand svg{width:44px;height:44px;flex-shrink:0}
h1{font-size:20px;color:#f0e2b0;letter-spacing:.02em;font-weight:600}
.sub{font-size:11px;color:#8a7d5c;letter-spacing:.14em;text-transform:uppercase;margin-top:3px}
.logout{font-size:12px;color:#8a7d5c;padding:8px 14px;border:1px solid #2a2318;border-radius:8px}
.logout:hover{border-color:#c9a961;color:#c9a961}
.panel{background:#0f0e0b;border:1px solid #2a2318;border-radius:14px;padding:24px;margin-bottom:20px}
.panel h2{font-size:12px;color:#c9a961;letter-spacing:.14em;text-transform:uppercase;margin-bottom:18px;font-weight:600}
input[type=password],textarea{width:100%;padding:14px 16px;background:#050505;border:1px solid #2a2318;border-radius:10px;color:#f0e2b0;font-size:14px;outline:none;font-family:inherit}
textarea{min-height:150px;font-family:ui-monospace,Menlo,monospace;font-size:13px;resize:vertical}
input:focus,textarea:focus{border-color:#c9a961}
button{padding:12px 22px;background:#c9a961;color:#0a0a0a;border:none;border-radius:10px;font-size:12px;font-weight:700;letter-spacing:.1em;cursor:pointer;text-transform:uppercase;font-family:inherit}
button:hover{background:#e0bf76}
button.ghost{background:transparent;color:#c9a961;border:1px solid #c9a961}
button.ghost:hover{background:#c9a961;color:#0a0a0a}
button:disabled{opacity:.5;cursor:wait}
.row{display:flex;gap:12px;margin-top:16px;flex-wrap:wrap}
.drop{border:2px dashed #2a2318;border-radius:12px;padding:34px 20px;text-align:center;cursor:pointer;transition:.2s;background:#080807}
.drop:hover,.drop.over{border-color:#c9a961;background:#100e08}
.drop .big{color:#c9a961;font-size:15px;font-weight:600;margin-bottom:8px}
.drop p{color:#8a7d5c;font-size:13px}
input[type=file]{display:none}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:12px}
.stat{background:#0d0c09;border:1px solid #2a2318;border-radius:10px;padding:14px}
.stat .k{font-size:10px;color:#8a7d5c;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px}
.stat .v{font-size:18px;color:#f0e2b0;font-weight:600}
.score{display:flex;align-items:center;gap:22px;margin-bottom:22px;flex-wrap:wrap}
.dial{width:104px;height:104px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700;position:relative;background:conic-gradient(var(--c) var(--p),#1a1712 0);color:#f0e2b0}
.dial::before{content:"";position:absolute;inset:8px;border-radius:50%;background:#0a0a0a}
.dial span{position:relative;z-index:2}
.verdict{font-size:22px;font-weight:700;letter-spacing:.04em}
.verdict.HIGH{color:#e07a5f}.verdict.MEDIUM{color:#e0b34a}.verdict.LOW{color:#7bc47b}
.flag{border-left:3px solid #c9a961;padding:14px 18px;margin-bottom:14px;background:#0d0c09;border-radius:0 10px 10px 0}
.flag.high{border-left-color:#e07a5f}.flag.medium{border-left-color:#e0b34a}
.flag h3{font-size:14px;color:#f0e2b0;margin-bottom:6px;text-transform:capitalize}
.flag .conf{font-size:10px;color:#8a7d5c;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px}
.flag p{font-size:13px;color:#c7b98a;line-height:1.6;margin-bottom:8px}
.flag .law{font-size:12px;color:#8a7d5c;padding-left:12px;border-left:1px solid #2a2318;margin:4px 0;line-height:1.5}
.flag .action{font-size:12px;color:#c9a961;margin-top:10px;font-style:italic}
pre{background:#050505;border:1px solid #2a2318;border-radius:10px;padding:16px;overflow-x:auto;font-size:12px;line-height:1.55;color:#c7b98a;font-family:ui-monospace,Menlo,monospace;white-space:pre-wrap;word-break:break-word}
.disc{font-size:12px;color:#8a7d5c;line-height:1.7;padding:16px;background:#0d0c09;border:1px solid #2a2318;border-radius:10px;margin-top:20px}
.disc strong{color:#c9a961}
.loading{color:#c9a961;font-size:13px;margin-top:16px;display:none;letter-spacing:.05em}
.loading.on{display:block}
.err{color:#e07a5f;font-size:13px;margin-top:12px;text-align:center}
footer{text-align:center;font-size:11px;color:#5a5142;padding:30px 0 10px;letter-spacing:.08em}
"""

def page_shell(title: str, body: str, extra_css: str = "") -> str:
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,__FAVICON__">
<style>{BASE_CSS}{extra_css}</style></head><body>{body}
<footer>Sovereign Intelligence Mesh · Satya Universe · Kerala, India</footer>
</body></html>"""
