"""spec.yaml + voice.mp3  ->  video.html (+ cover.html, timing.json)

Usage: python tools/build.py content/2026-11/<slug>
"""
import sys, json, re, html, pathlib, yaml
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from themes import THEMES
from align import align
from art import ART

E = html.escape


def rich(s):
    """*good*  ~bad~  -> highlighted spans"""
    s = E(s).replace("&lt;br&gt;", "<br>").replace("\n", "<br>")
    s = re.sub(r"\*(.+?)\*", r'<em>\1</em>', s)
    s = re.sub(r"~(.+?)~", r'<em class="b">\1</em>', s)
    return s


def tone(t, th):
    return {"good": th["good"], "bad": th["bad"], "mut": th["mut"], "ink": th["ink"]}.get(t or "ink", t or th["ink"])


class Ctx:
    def __init__(s, t0, t1, L, th, fx=None):
        s.t0, s.t1, s.L, s.th, s.fx = t0, t1, L, th, fx

    def at(s, v, default):
        """int -> start of that line in the scene; '+1.2' -> seconds after scene start."""
        if v is None:
            v = default
        if isinstance(v, str) and v.startswith("+"):
            return round(s.t0 + float(v[1:]), 3)
        if isinstance(v, int) and 0 <= v < len(s.L):
            return round(s.L[v], 3)
        return round(s.t0 + float(v), 3)


def A(t, anim="up", dur=None, extra=""):
    d = f' data-dur="{dur}"' if dur else ""
    return f'data-at="{t}" data-anim="{anim}"{d} {extra}'


def count_span(c, value, at, pre="", suf="", dec=0, sep=False, frm=0, dur=2.2):
    return (f'<span data-count="{value}" data-from="{frm}" data-cat="{at}" data-cdur="{dur}" data-dec="{dec}" '
            f'data-pre="{E(pre)}" data-suf="{E(suf)}"{" data-sep" if sep else ""}></span>')


# ---------------- components ----------------
def c_bignum(v, c):
    th = c.th; col = tone(v.get("tone", "bad"), th)
    size = v.get("size", 110 if len(str(v["value"])) > 8 else 220)
    num = count_span(c, v["value"], c.t0 + .3, v.get("prefix", ""), v.get("suffix", ""), v.get("decimals", 0), v.get("sep", False))
    out = f'<div class="lbl" {A(c.t0 + .1)}>{E(v.get("label", ""))}</div>'
    out += f'<div class="num" style="font-size:{size}px;color:{col};margin-top:24px;text-shadow:0 0 60px {col}55" {A(c.t0 + .2, "zoom", .9)}>{num}</div>'
    if v.get("note"):
        out += f'<div class="note" {A(c.at(v.get("note_at"), "+1.4"))}>{E(v["note"])}</div>'
    return out


def c_title(v, c):
    out = ""
    if v.get("kicker"):
        out += f'<div class="lbl" style="font-size:40px" {A(c.t0 + .05)}>{E(v["kicker"])}</div>'
    out += f'<div class="disp" style="font-size:{v.get("size", 260)}px;line-height:1;text-align:center" {A(c.t0 + .05, "zoom", .6)}>{rich(v["text"])}</div>'
    if v.get("underline", True):
        out += (f'<svg width="760" height="40" viewBox="0 0 760 40"><path d="M10 26 C 200 6, 520 6, 750 22" stroke="{c.th["bad"]}" '
                f'stroke-width="12" fill="none" stroke-linecap="round" {A(c.t0 + .5, "draw", .7)}/></svg>')
    if v.get("sub"):
        out += f'<div class="note" {A(c.at(v.get("sub_at"), "+.8"))}>{rich(v["sub"])}</div>'
    return out


def c_bars(v, c):
    """Vertical bars; negative values hang below the axis."""
    th = c.th; items = v["items"]; n = len(items)
    mx = max(abs(i["value"]) for i in items) or 1
    hasneg = any(i["value"] < 0 for i in items)
    H = 340 if hasneg else 480; axis = 460 if hasneg else 600; W = 860; bw = min(240, int(W / n * .55))
    out = f'<div class="lbl" {A(c.t0 + .05)}>{E(v.get("label", ""))}</div><div style="position:relative;width:{W}px;height:{axis + (240 if hasneg else 90)}px;margin-top:60px">'
    out += f'<div style="position:absolute;left:0;right:0;top:{axis}px;height:3px;background:{th["mut"]};opacity:.6;transform-origin:left" {A(c.t0 + .1, "growx", .9)}></div>'
    for k, it in enumerate(items):
        x = int(W / n * (k + .5) - bw / 2)
        t = c.at(it.get("at"), f"+{.4 + k * .6}")
        h = max(8, int(H * abs(it["value"]) / mx)); col = tone(it.get("tone", "good" if it["value"] >= 0 else "bad"), th)
        if it["value"] >= 0:
            out += f'<div style="position:absolute;left:{x}px;width:{bw}px;top:{axis - h}px;height:{h}px;border-radius:20px 20px 0 0;background:{col};transform-origin:bottom" {A(t, "growy", 1.3)}></div>'
            ly = axis - h - 110
        else:
            out += f'<div style="position:absolute;left:{x}px;width:{bw}px;top:{axis + 3}px;height:{h}px;border-radius:0 0 20px 20px;background:{col};transform-origin:top" {A(t, "growy", 1.2)}></div>'
            ly = axis - 100
        out += f'<div style="position:absolute;left:{x - 60}px;width:{bw + 120}px;top:{ly}px;text-align:center" {A(t + .3, "pop")}><span class="num" style="font-size:{v.get("valsize", 68)}px;color:{col}">{E(it.get("display", str(it["value"])))}</span></div>'
        ny = axis + 20 if it["value"] >= 0 else axis + h + 20
        out += f'<div style="position:absolute;left:{x - 60}px;width:{bw + 120}px;top:{ny}px;text-align:center;font-weight:700;font-size:32px;color:{th["mut"]}" {A(t, "up")}>{E(it["name"])}</div>'
    return out + "</div>"


def c_split(v, c):
    """One horizontal bar split into parts (what a total is made of)."""
    th = c.th; parts = v["parts"]; tot = sum(p["value"] for p in parts)
    out = f'<div class="lbl" {A(c.t0 + .05)}>{E(v.get("label", ""))}</div>'
    out += f'<div style="width:920px;height:170px;margin-top:60px;display:flex;border-radius:26px;overflow:hidden;transform-origin:left" {A(c.t0 + .3, "growx", 1.2)}>'
    for p in parts:
        bg = (f'repeating-linear-gradient(135deg,{th["mut"]}55 0 18px,{th["mut"]}22 18px 36px)' if p.get("hatch") else tone(p.get("tone", "bad"), th))
        out += f'<div style="width:{p["value"] / tot * 100:.2f}%;height:100%;background:{bg};border-right:4px solid {th["bg"]}"></div>'
    out += '</div><div style="width:920px;display:flex;justify-content:space-between;margin-top:30px">'
    for k, p in enumerate(parts):
        al = "left" if k == 0 else "right"
        out += f'<div style="text-align:{al}" {A(c.t0 + 1.0 + k * .5)}><div class="num" style="font-size:80px;color:{tone(p.get("tone", "ink"), th)}">{E(p["display"])}</div><div class="note" style="margin:0">{E(p["name"])}</div></div>'
    return out + "</div>"


def c_flow(v, c):
    th = c.th; out = ""
    for k, it in enumerate(v["items"]):
        t = c.at(it.get("at"), k if k < len(c.L) else f"+{k * 2}")
        if k:
            out += f'<svg width="40" height="80" viewBox="0 0 40 80"><path d="M20 6 V 70 M8 58 L20 72 L32 58" stroke="{th["mut"]}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round" {A(t - .4, "draw", .4)}/></svg>'
        col = tone(it.get("tone", "ink"), th)
        out += (f'<div class="card" {A(t, "left" if k % 2 == 0 else "right")}><div class="ic" style="background:{col}22;color:{col}">{E(it.get("icon", str(k + 1)))}</div>'
                f'<div class="tx"><b>{E(it["title"])}</b><span>{E(it.get("sub", ""))}</span></div></div>')
    return out


def c_compare(v, c):
    """Two blocks whose AREA shows the ratio."""
    th = c.th; a, b = v["items"]; r = (b["value"] / a["value"]) ** .5
    sa = 170; sb = min(380, int(sa * r))
    out = '<div style="display:flex;align-items:flex-end;gap:70px">'
    for it, s, t, col in ((a, sa, c.t0 + .1, th["ink"]), (b, sb, c.at(b.get("at"), "+1.0"), th["bad"])):
        out += (f'<div style="text-align:center" {A(t)}><div style="width:{s}px;height:{s}px;border-radius:{s // 7}px;background:{col};margin:0 auto" {A(t + .1, "pop", 1)}></div>'
                f'<div class="num" style="font-size:56px;margin-top:24px">{E(it["display"])}</div><div class="note" style="margin:0">{E(it["name"])}</div></div>')
    return out + "</div>"


def c_statement(v, c):
    th = c.th; out = ""
    for k, it in enumerate(v["items"]):
        t = c.at(it.get("at"), f"+{k * 1.5}")
        col = tone(it.get("tone", "ink"), th)
        size = it.get("size", 90)
        inner = f'<div class="disp" style="font-size:{size}px;line-height:1.05;color:{col};text-align:center">{rich(it["text"])}</div>'
        if it.get("strike"):
            st = c.at(it["strike_at"], 0) if it.get("strike_at") is not None else round(t + 1.2, 3)
            inner = (f'<div style="position:relative">{inner}<svg viewBox="0 0 100 10" preserveAspectRatio="none" style="position:absolute;left:-2%;width:104%;top:40%;height:20px">'
                     f'<path d="M0 6 L100 4" stroke="{th["bad"]}" fill="none" vector-effect="non-scaling-stroke" style="stroke-width:10" {A(st, "draw", .5)}/></svg></div>')
        out += f'<div style="margin:24px 0" {A(t, it.get("anim", "pop"), .8)}>{inner}</div>'
    return out


def c_gauge(v, c):
    th = c.th; f, to = v["from"], v["to"]; t = c.at(v.get("at"), "+2.0")
    deg = lambda p: -90 + 180 * p / 100
    return (f'<div class="lbl" {A(c.t0 + .1)}>{E(v.get("label", ""))}</div>'
            f'<div style="position:relative;width:760px;height:540px;margin-top:30px" {A(c.t0 + .2)}>'
            f'<svg width="760" height="420" viewBox="0 0 760 420" style="position:absolute;inset:0"><path d="M60 380 A 320 320 0 0 1 700 380" stroke="{th["mut"]}33" stroke-width="46" fill="none" stroke-linecap="round"/>'
            f'<path d="M60 380 A 320 320 0 0 1 700 380" stroke="{th["bad"]}" stroke-width="46" fill="none" stroke-linecap="round" {A(c.t0 + .3, "draw", 1.4)}/></svg>'
            f'<div style="position:absolute;left:376px;top:110px;width:8px;height:272px;border-radius:8px;background:{th["ink"]};transform-origin:bottom center" data-rot="{deg(to)}" data-rfrom="{deg(f)}" data-rat="{t}" data-rdur="1.6"></div>'
            f'<div style="position:absolute;left:356px;top:360px;width:48px;height:48px;border-radius:50%;background:{th["ink"]}"></div>'
            f'<div style="position:absolute;left:0;right:0;top:420px;text-align:center"><span class="num" style="font-size:96px">{count_span(c, to, t, "", v.get("suffix", "%"), 0, False, f, 1.6)}</span></div></div>'
            f'<div class="note" {A(t + .3)}>{E(v.get("note", ""))}</div>')


def c_checklist(v, c):
    th = c.th; t = c.at(v.get("at"), "+.8"); out = f'<div class="card" style="flex-direction:column;align-items:stretch;gap:0" {A(c.t0 + .05)}>'
    out += f'<div style="font-family:monospace;font-size:28px;color:{th["mut"]};margin-bottom:16px">{E(v.get("title", ""))}</div>'
    for k, it in enumerate(v["items"]):
        out += f'<div class="step" {A(t + k * .45, "left")}><i>✓</i>{E(it)}</div>'
    return out + "</div>"


def c_cta(v, c):
    t = c.t0; tc = t + 1.15
    c.fx["pops"].append(round(tc, 2))
    return (f'<div class="ctabox" {A(t + .05, "pop", .6)}>'
            f'<div class="avatar"><span class="lw">W</span></div>'
            f'<div class="disp" style="font-size:64px;margin-top:26px;letter-spacing:1px">WEALTH IN WHISPERS</div>'
            f'<div style="font-size:34px;color:var(--mut);margin-top:6px">{E(v.get("handle", "@wealthinwhispers"))}</div>'
            f'<div style="font-size:40px;font-weight:700;margin-top:30px;text-align:center">{rich(v.get("text", "Business breakdowns, *in under a minute*."))}</div>'
            f'<div class="fbtn" data-at="{tc}" data-anim="press" style="position:relative;margin-top:44px">'
            f'<span class="f1" {A(t + .3, "fade", .3, f'data-out="{tc}" data-outdur="0.15"')}>{E(v.get("button", "+ FOLLOW"))}</span>'
            f'<span class="f2" {A(tc, "pop", .35)}>{E(v.get("button_done", "✓ FOLLOWING"))}</span></div>'
            f'<div style="position:absolute;left:640px;top:600px;z-index:6" {A(t + .45, "cursor", .7)}>'
            f'<svg width="70" height="90" viewBox="0 0 24 30"><path d="M2 2 L2 24 L8 18 L12 28 L16 26 L12 17 L20 17Z" fill="#fff" stroke="#000" stroke-width="1.6"/></svg></div>'
            f'<div style="margin-top:30px;font-size:30px;color:var(--mut)" {A(tc + .3, "up", .5)}>{E(v.get("foot", "New breakdown every day · Links in bio"))}</div></div>')


def c_hero(v, c):
    T = lambda x: c.at(x, 0)
    art = ART[v["art"]](T, v)
    out = f'<div class="heroart" style="top:{v.get("art_top", 0)}px">{art}</div>'
    if v.get("head"):
        ht = c.at(v.get("head_at"), "+.35")
        out += f'<div class="herohead disp" style="font-size:{v.get("size", 92)}px;color:{tone(v.get("tone", "ink"), c.th)}" {A(ht, "up", .6)}>{rich(v["head"])}</div>'
        if v.get("hit_head"):
            c.fx["hits"].append(ht)
    for b in v.get("badges", []):
        bt = c.at(b.get("at"), "+.9")
        c.fx["pops"].append(bt)
        out += (f'<div class="badge" style="left:{b.get("x", 60)}px;top:{b.get("y", 60)}px" {A(bt, "pop", .45)}>'
                f'<i style="background:{tone(b.get("tone", "good"), c.th)}"></i>{rich(b["text"])}</div>')
    for h in v.get("hits", []):
        c.fx["hits"].append(c.at(h, 0))
    return out


COMP = dict(hero=c_hero, bignum=c_bignum, title=c_title, bars=c_bars, split=c_split, flow=c_flow, compare=c_compare,
            statement=c_statement, gauge=c_gauge, checklist=c_checklist, cta=c_cta)


def stamp(s, c):
    t = c.at(s.get("at"), "+1.5")
    return (f'<div style="position:absolute;top:{s.get("top", 40)}px;{s.get("side", "right")}:{s.get("x", 100)}px;z-index:5" {A(t, "stamp", .55, f"data-rot=\"{s.get("rot", -6)}\"")}>'
            f'<div class="stamp">{E(s["text"])}</div></div>')


CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:%(bg)s;font-family:%(body)s;color:%(ink)s}
#stage{position:absolute;inset:0;overflow:hidden}.bgfx{position:absolute}
.logo{position:absolute;top:78px;right:62px;display:flex;align-items:center;gap:8px;font-family:Anton;color:%(logo)s;transform:skewX(-10deg);z-index:9}
.logo .lw{font-size:86px;line-height:.8;letter-spacing:-6px}.logo .lt{font-size:30px;line-height:.92;letter-spacing:.5px}
.kicker{position:absolute;top:96px;left:62px;font-weight:700;font-size:26px;letter-spacing:5px;color:%(mut)s;z-index:9}
#prog{position:absolute;left:0;top:0;height:6px;width:100%%;background:%(accent)s;transform-origin:left;z-index:9}
.scene{position:absolute;left:0;right:0;top:330px;height:830px;display:flex;flex-direction:column;align-items:center;justify-content:center}
.lbl{font-weight:700;font-size:30px;letter-spacing:6px;color:%(mut)s;text-transform:uppercase;text-align:center}
.num{font-family:%(num)s;font-weight:900;font-variant-numeric:tabular-nums;letter-spacing:-3px}
.disp{font-family:%(display)s;font-weight:900;letter-spacing:-1px}
.note{margin-top:40px;font-size:32px;color:%(mut)s;text-align:center}
.cap{position:absolute;left:80px;right:80px;top:1200px;height:300px;display:flex;justify-content:center;text-align:center}
.say{font-weight:%(capweight)s;font-size:64px;line-height:1.15;letter-spacing:-1.5px}.say .w{display:inline-block}
.card{width:840px;padding:34px 44px;border-radius:32px;background:%(card)s;border:1.5px solid %(edge)s;display:flex;align-items:center;gap:34px;box-shadow:0 30px 80px rgba(0,0,0,.25)}
.card .ic{width:96px;height:96px;border-radius:24px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:34px;flex:none}
.card .tx b{display:block;font-size:42px;font-weight:800;letter-spacing:-1px}.card .tx span{font-size:28px;color:%(mut)s}
.step{display:flex;align-items:center;gap:22px;font-size:38px;font-weight:600;padding:14px 0}
.step i{width:52px;height:52px;border-radius:50%%;background:%(good)s;color:%(bg)s;font-style:normal;font-weight:900;font-size:30px;display:flex;align-items:center;justify-content:center}
.chip{display:inline-block;padding:18px 36px;border-radius:999px;background:%(accent)s;color:%(bg)s;font-weight:900;font-size:36px;letter-spacing:2px}
.stamp{border:6px solid %(good)s;color:%(good)s;background:%(bg)s;font-family:Anton;font-size:90px;padding:4px 28px;border-radius:16px;white-space:nowrap}
.src{position:absolute;bottom:330px;left:0;right:0;text-align:center;font-size:24px;color:%(src)s;letter-spacing:1px}
em{font-style:normal;%(emcss)s} em.b{%(em2css)s}
:root{--bg:%(bg)s;--ink:%(ink)s;--mut:%(mut)s;--good:%(good)s;--bad:%(bad)s;--card:%(card)s;--card2:%(card2)s;--edge:%(edge)s}
svg [data-anim],svg [data-loop]{transform-box:fill-box;transform-origin:center}
.push{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.heroart{position:absolute;left:0;right:0;display:flex;justify-content:center}
.herohead{position:absolute;left:60px;right:60px;bottom:10px;text-align:center;line-height:1.02;text-shadow:0 10px 40px rgba(0,0,0,.35)}
.badge{position:absolute;display:flex;align-items:center;gap:14px;padding:16px 28px;border-radius:999px;background:var(--card2);border:2px solid var(--edge);font-weight:800;font-size:36px;box-shadow:0 20px 50px rgba(0,0,0,.3);z-index:4}
.badge i{width:16px;height:16px;border-radius:50%%}
.artback{position:absolute;inset:-80px;display:flex;align-items:center;justify-content:center;opacity:.16;z-index:0}
.sweep{position:absolute;top:-200px;left:0;width:260px;height:2400px;background:linear-gradient(90deg,transparent,%(accent)s55,#ffffffaa,%(accent)s55,transparent);z-index:8;mix-blend-mode:screen}
.ctabox{display:flex;flex-direction:column;align-items:center;position:relative}
.avatar{width:230px;height:230px;border-radius:50%%;background:%(bg)s;border:8px solid %(logo)s;display:flex;align-items:center;justify-content:center;box-shadow:0 0 90px %(logo)s66}
.avatar .lw{font-family:Anton;font-size:150px;color:%(logo)s;transform:skewX(-10deg);line-height:1}
.fbtn{width:560px;height:124px;border-radius:999px;background:%(bad)s;display:flex;align-items:center;justify-content:center;box-shadow:0 20px 60px %(bad)s66}
.fbtn span{position:absolute;font-weight:900;font-size:50px;letter-spacing:2px;color:#fff}
.dot{position:absolute;border-radius:50%%;background:%(accent)s}
"""


def theme_css(th):
    if th["emstyle"] == "marker":
        emcss = f"background:linear-gradient(transparent 58%,{th['em']} 58%);padding:0 4px"
        em2 = f"background:linear-gradient(transparent 58%,{th['em2']} 58%);padding:0 4px"
    else:
        emcss, em2 = f"color:{th['em']}", f"color:{th['em2']}"
    return CSS % dict(th, emcss=emcss, em2css=em2)


import random as _r
_g = _r.Random(7)
PARTICLES = "".join(f'<div class="dot" style="left:{_g.randint(0, 1060)}px;top:{_g.randint(1900, 2100)}px;width:{_g.choice([4, 5, 6, 8])}px;height:{_g.choice([4, 5, 6, 8])}px" data-loop="drift" data-spd="{_g.uniform(.035, .07):.3f}" data-amp="{_g.randint(10, 40)}" data-ph="{_g.random():.3f}" data-op="{_g.uniform(.25, .6):.2f}"></div>' for _ in range(34))
LOGO = '<div class="logo"><span class="lw">W</span><span class="lt">WEALTH IN<br>WHISPERS</span></div>'


LAND_CSS = """html,body{width:1920px;height:1080px}
.logo{top:40px;right:56px}.logo .lw{font-size:66px}.logo .lt{font-size:23px}
.kicker{top:50px;left:60px}
.scene{top:80px;height:780px}
.cap{top:872px;height:190px;left:200px;right:200px}
.say{font-size:48px;letter-spacing:-1px}
.src{bottom:12px;font-size:18px}
.heroart{left:40px;right:auto;width:980px;top:0;bottom:0;align-items:center}
.herohead{left:1030px;right:100px;top:230px;bottom:auto;text-align:left}
.artback{inset:-40px -260px}
.sweep{width:360px}
.chap{position:absolute;left:60px;top:44px;font-weight:800;font-size:22px;letter-spacing:5px;color:%(mut)s;z-index:9}
"""


def particles(w):
    g = _r.Random(7)
    n = 34 if w < 1500 else 48
    return "".join(f'<div class="dot" style="left:{g.randint(0, w - 20)}px;top:{g.randint(1900, 2100)}px;width:{g.choice([4, 5, 6, 8])}px;height:{g.choice([4, 5, 6, 8])}px" data-loop="drift" data-spd="{g.uniform(.035, .07):.3f}" data-amp="{g.randint(10, 40)}" data-ph="{g.random():.3f}" data-op="{g.uniform(.25, .6):.2f}"></div>' for _ in range(n))


def page(th, body, total, eng="../../../engine/engine.js", extra_js="", land=False):
    css = theme_css(th) + (LAND_CSS % th if land else "")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div id="stage">
{th['background']}{particles(1920 if land else 1080)}<div id="prog"></div>{LOGO}{body}</div>
<script>window.TOTAL={total};
window.ambient=function(t){{const A=document.getElementById('bgA'),B=document.getElementById('bgB'),Cc=document.getElementById('bgC');{th['ambient']}}};{extra_js}</script>
<script src="{eng}"></script></body></html>"""


def build(folder):
    folder = pathlib.Path(folder)
    spec = yaml.safe_load((folder / "spec.yaml").read_text())
    th = THEMES[spec.get("theme", "dark")]
    norm = [l if isinstance(l, dict) else {"show": l, "say": re.sub(r"[*~]", "", l)} for s in spec["scenes"] for l in s["lines"]]
    lines = [l["show"] for l in norm]
    timing = align(folder / "voice.mp3", [l["say"] for l in norm])
    if spec.get("starts"):
        st = spec["starts"]; dur = timing["duration"]
        timing["lines"] = [{"start": st[k], "end": round((st[k + 1] - .3) if k + 1 < len(st) else dur - .2, 3)} for k in range(len(st))]
    (folder / "timing.json").write_text(json.dumps(timing, indent=1))
    total = timing["duration"]
    body, i = "", 0
    fx = {"whoosh": [], "hits": [], "pops": [], "music": spec.get("music", "tech")}
    if spec.get("kicker"):
        body += f'<div class="kicker">{E(spec["kicker"])}</div>'
    caps = ""
    starts = [x["start"] for x in timing["lines"]]
    scene_starts = []
    for si, sc in enumerate(spec["scenes"]):
        n = len(sc["lines"]); L = starts[i:i + n]
        t0 = max(0, L[0] - .1); i += n
        t1 = (starts[i] - .25) if i < len(starts) else None
        scene_starts.append(t0)
        c = Ctx(t0, t1, L, th, fx)
        v = sc["visual"]
        inner = COMP[v["type"]](v, c) + (stamp(v["stamp"], c) if v.get("stamp") else "")
        if v.get("stamp"):
            fx["hits"].append(c.at(v["stamp"].get("at"), "+1.5"))
        if v["type"] == "bignum":
            fx["hits"].append(round(c.t0 + .3, 2))
        if v.get("art") and v["type"] != "hero":
            ab = dict(v["art"]) if isinstance(v["art"], dict) else {"name": v["art"]}
            ab.setdefault("w", 1000)
            inner = f'<div class="artback">{ART[ab["name"]](lambda x: c.at(x, 0), ab)}</div>' + inner
        out = f' data-out="{t1}" data-outmode="zoom" data-outdur="0.35"' if t1 else ""
        if si > 0:
            body += f'<div class="sweep" data-at="{max(0, t0 - .25):.3f}" data-anim="sweep" data-dur="0.55"></div>'
            fx["whoosh"].append(round(max(0, t0 - .3), 2))
        body += f'<div class="scene" data-at="{t0}" data-anim="enter" data-dur="0.55"{out}><div class="push" data-push="{t0},{t1 or total}">{inner}</div></div>\n'
    for k, ln in enumerate(timing["lines"]):
        nxt = timing["lines"][k + 1]["start"] - .12 if k + 1 < len(timing["lines"]) else None
        out = f' data-out="{nxt}" data-outdur="0.25"' if nxt else ""
        caps += (f'<div class="cap" data-at="{max(0, ln["start"] - .05):.3f}" data-anim="fade" data-dur="0.01"{out}>'
                 f'<div class="say" data-at="{ln["start"]:.3f}" data-end="{ln["end"]:.3f}">{rich(lines[k])}</div></div>\n')
    body += caps + f'<div class="src">{E(spec.get("source", "Not financial advice"))}</div>'
    import os
    eng = os.path.relpath(pathlib.Path(__file__).resolve().parent.parent / "engine" / "engine.js", folder.resolve())
    land = spec.get("format") == "landscape"
    if land:
        chaps = []
        for sc, st0 in zip(spec["scenes"], scene_starts):
            if sc.get("chapter"):
                t = 0 if not chaps else int(st0)
                chaps.append(f"{t // 60}:{t % 60:02d} {sc['chapter']}")
                body += f'<div class="chap" data-at="{st0:.3f}" data-anim="fade" data-dur="0.4"' + (f' data-out="{nxt:.3f}"' if (nxt := next((x for c2, x in zip(spec["scenes"], scene_starts) if c2.get("chapter") and x > st0), None)) else "") + f'>{E(sc["chapter"]).upper()}</div>'
        (folder / "chapters.txt").write_text("\n".join(chaps) + "\n")
        timing["w"], timing["h"] = 1920, 1080
        (folder / "timing.json").write_text(json.dumps(timing, indent=1))
    (folder / "video.html").write_text(page(th, body, total, eng, land=land))
    (folder / "fx.json").write_text(json.dumps(fx))
    # cover / thumbnail
    cv = spec.get("cover", {})
    cover = (f'<div class="scene" style="top:300px;height:900px">'
             f'<div class="disp" style="font-size:{cv.get("size1", 200)}px;line-height:1;color:{tone(cv.get("tone", "bad"), th)};text-align:center">{rich(cv.get("line1", ""))}</div>'
             f'<div class="disp" style="font-size:{cv.get("size2", 120)}px;line-height:1.05;margin-top:30px;text-align:center">{rich(cv.get("line2", ""))}</div>'
             f'<div class="lbl" style="margin-top:50px">{E(cv.get("line3", ""))}</div></div>')
    (folder / "cover.html").write_text(page(th, cover, 1, eng))
    print(f"built {folder}: {len(lines)} lines, {total:.2f}s, theme={spec.get('theme', 'dark')}")
    return spec, total


if __name__ == "__main__":
    build(sys.argv[1])
