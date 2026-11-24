"""Render a WIW-branded ranked-bar infographic (1080x1350 JPG) from a folder's infographic.yaml.

  python tools/infographic.py content/2026-11/<slug>    -> <slug>/image.jpg
infographic.yaml: kicker, title, sub, unit_note, rows[{name, value, display, tone(good|bad|mut), note}], stats[{value,label}], source
"""
import sys, pathlib, yaml, html, asyncio
from playwright.async_api import async_playwright

LIME, BG1, BG2, INK, MUT, BAD = "#c9de3c", "#232c0b", "#0a0d04", "#f3f1e6", "#9aa184", "#ff6b5a"

def page(d):
    rows = d["rows"]; mx = max(abs(r["value"]) for r in rows)
    rh = min(150, int((780 if not d.get("stats") else 600) / len(rows)))
    out = []
    for i, r in enumerate(rows, 1):
        tone = {"bad": BAD, "mut": "#6e7556"}.get(r.get("tone"), LIME)
        w = max(4, abs(r["value"]) / mx * 100)
        note = f'<div class="note">{html.escape(r["note"])}</div>' if r.get("note") else ""
        out.append(f'''<div class="row" style="height:{rh}px"><div class="rk">{i}</div>
<div class="nm"><div class="n">{html.escape(r["name"])}</div>{note}</div>
<div class="barw"><div class="bar" style="width:{w:.1f}%;background:linear-gradient(90deg,{tone}cc,{tone})"></div></div>
<div class="val" style="color:{tone}">{html.escape(r["display"])}</div></div>''')
    stats = "".join(f'<div class="st"><div class="sv">{html.escape(s["value"])}</div><div class="sl">{html.escape(s["label"])}</div></div>' for s in d.get("stats", []))
    stats = f'<div class="stats">{stats}</div>' if stats else ""
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden;font-family:Inter,sans-serif;color:{INK};
background:radial-gradient(ellipse at 20% 0%,#3a4812 0%,transparent 55%),linear-gradient(170deg,{BG1},{BG2} 70%);position:relative}}
body:before{{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(201,222,60,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(201,222,60,.05) 1px,transparent 1px);background-size:60px 60px}}
.logo{{position:absolute;top:56px;right:60px;display:flex;align-items:center;gap:8px;font-family:Anton;color:{LIME};transform:skewX(-10deg)}}
.logo .lw{{font-size:70px;line-height:.8;letter-spacing:-5px}}.logo .lt{{font-size:24px;line-height:.92}}
.wrap{{position:absolute;inset:60px 60px 50px 60px;display:flex;flex-direction:column}}
.kick{{font-weight:800;letter-spacing:4px;font-size:22px;color:{LIME};text-transform:uppercase;margin-top:8px}}
h1{{font-family:Anton;font-weight:400;font-size:{d.get("title_size",92)}px;line-height:1.02;margin:22px 0 10px;max-width:960px;text-transform:uppercase}}
h1 em{{font-style:normal;color:{LIME}}}
.sub{{font-size:28px;color:{MUT};margin-bottom:28px}}
.head{{display:flex;font-size:20px;letter-spacing:2px;color:{MUT};text-transform:uppercase;border-bottom:2px solid rgba(201,222,60,.25);padding-bottom:10px}}
.head .a{{width:430px;padding-left:66px}}.head .b{{flex:1}}.head .c{{width:170px;text-align:right}}
.row{{display:flex;align-items:center;border-bottom:1px solid rgba(255,255,255,.08)}}
.rk{{width:66px;font-family:Anton;font-size:44px;color:{MUT}}}
.nm{{width:364px}}.n{{font-size:38px;font-weight:800;line-height:1.05}}.note{{font-size:20px;color:{MUT};margin-top:4px}}
.barw{{flex:1;height:30px;margin-right:22px}}.bar{{height:100%;border-radius:15px;box-shadow:0 0 24px rgba(201,222,60,.25)}}
.val{{width:170px;text-align:right;font-family:Anton;font-size:50px}}
.stats{{display:flex;gap:20px;margin-top:26px}}.st{{flex:1;background:rgba(201,222,60,.08);border:1px solid rgba(201,222,60,.25);border-radius:22px;padding:20px 24px}}
.sv{{font-family:Anton;font-size:52px;color:{LIME}}}.sl{{font-size:22px;color:{MUT};margin-top:2px}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font-size:19px;color:{MUT};gap:30px}}
.foot b{{color:{LIME};font-size:24px;white-space:nowrap}}
</style></head><body>
<div class="logo"><span class="lw">W</span><span class="lt">WEALTH IN<br>WHISPERS</span></div>
<div class="wrap"><div class="kick">{html.escape(d["kicker"])}</div><h1>{d["title"]}</h1><div class="sub">{html.escape(d.get("sub",""))}</div>
<div class="head"><div class="a">{html.escape(d.get("col1","Company"))}</div><div class="b"></div><div class="c">{html.escape(d.get("col3",""))}</div></div>
{"".join(out)}{stats}
<div class="foot"><div>{html.escape(d["source"])}</div><b>@wealthinwhisper</b></div></div></body></html>'''

async def main(folder):
    fp = pathlib.Path(folder); d = yaml.safe_load((fp / "infographic.yaml").read_text())
    (fp / "image.html").write_text(page(d))
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        await pg.goto((fp / "image.html").resolve().as_uri()); await pg.evaluate("document.fonts.ready")
        await pg.screenshot(path=str(fp / "image.jpg"), type="jpeg", quality=92); await b.close()
    print("wrote", fp / "image.jpg")

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
