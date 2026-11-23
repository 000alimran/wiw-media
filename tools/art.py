"""Animated SVG illustrations for `hero` scenes and `art:` backdrops.

Every function takes (T, v): T(x) turns a scene-relative offset into an absolute time
(T(0) = scene start, T(1) = start of the scene's 2nd line, T("+1.2") = 1.2s after scene start),
and v is the visual dict (for optional text params). Colors come from CSS vars set by the theme.
Loop motion uses data-loop (float, sway, spin, pulse, blink, flicker, fall, rise, glow, slide).
No brand logos: everything is generic.
"""


def a(t, anim="up", dur=None, extra=""):
    d = f' data-dur="{dur}"' if dur else ""
    return f'data-at="{t:.3f}" data-anim="{anim}"{d} {extra}'


def loop(kind, spd=1, amp=10, ph=0, extra=""):
    return f'data-loop="{kind}" data-spd="{spd}" data-amp="{amp}" data-ph="{ph}" {extra}'


SVG = '<svg viewBox="0 0 600 600" width="{w}" height="{w}" style="overflow:visible">{body}</svg>'


def gpu(T, v):
    t = T(0)
    pins = "".join(
        f'<rect x="{150 + i * 30}" y="{y}" width="12" height="34" rx="3" fill="var(--mut)" {a(t + .15 + i * .03, "growy", .4)}/>'
        for i in range(10) for y in (96, 470))
    pins += "".join(
        f'<rect x="{x}" y="{150 + i * 30}" width="34" height="12" rx="3" fill="var(--mut)" {a(t + .15 + i * .03, "growx", .4)}/>'
        for i in range(10) for x in (96, 470))
    traces = ""
    for k, (x1, y1, x2, y2) in enumerate([(300, 96, 300, -40), (504, 300, 640, 300), (300, 504, 300, 640), (96, 300, -40, 300),
                                          (220, 96, 160, -20), (380, 504, 440, 620), (504, 220, 620, 160), (96, 380, -20, 440)]):
        traces += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="var(--good)" stroke-width="4" stroke-linecap="round" opacity=".7" {a(t + .5 + k * .06, "draw", .7)}/>'
        traces += f'<circle cx="{x2}" cy="{y2}" r="9" fill="var(--good)" {a(t + 1.1 + k * .06, "pop", .4)}/>'
    return SVG.format(w=v.get("w", 640), body=f"""
<defs><radialGradient id="gg"><stop offset="0" stop-color="var(--good)" stop-opacity=".9"/><stop offset="1" stop-color="var(--good)" stop-opacity="0"/></radialGradient></defs>
{traces}
<g {a(t, "pop", .6)}><g {loop("float", .25, 8)}>
<circle cx="300" cy="300" r="260" fill="url(#gg)" opacity=".35" {loop("glow", .5)}/>
{pins}
<rect x="130" y="130" width="340" height="340" rx="36" fill="var(--card2)" stroke="var(--edge)" stroke-width="3"/>
<rect x="185" y="185" width="230" height="230" rx="22" fill="var(--good)" opacity=".16"/>
<rect x="185" y="185" width="230" height="230" rx="22" fill="none" stroke="var(--good)" stroke-width="5" {a(t + .3, "draw", .9)}/>
<g {loop("glow", .7)}><text x="300" y="330" text-anchor="middle" font-family="Anton" font-size="96" fill="var(--good)">AI</text></g>
</g></g>""")


def servers(T, v):
    t = T(0)
    racks = ""
    for r, x in enumerate((70, 230, 390)):
        units = ""
        for u in range(7):
            y = 120 + u * 56
            leds = "".join(f'<circle cx="{x + 20 + j * 16}" cy="{y + 22}" r="5" fill="var({"--good" if (u + j + r) % 3 else "--bad"})" {loop("blink", 1.2 + ((u * 7 + j * 3 + r) % 5) * .35, ph=((u * 13 + j * 5 + r * 3) % 10) / 10)}/>' for j in range(3))
            units += f'<g {a(t + .1 + r * .12 + u * .05, "left", .45)}><rect x="{x}" y="{y}" width="140" height="44" rx="8" fill="var(--card2)" stroke="var(--edge)" stroke-width="2"/>{leds}<rect x="{x + 76}" y="{y + 18}" width="50" height="8" rx="4" fill="var(--mut)" opacity=".5"/></g>'
        racks += f'<g {a(t + r * .12, "up", .5)}><rect x="{x - 12}" y="96" width="164" height="420" rx="16" fill="none" stroke="var(--edge)" stroke-width="3"/>{units}</g>'
    beams = "".join(f'<rect x="{60 + i * 120}" y="-80" width="6" height="170" rx="3" fill="var(--good)" opacity=".5" {loop("fall", .6 + i * .1, ph=i * .23, extra="data-range=\"640\"")}/>' for i in range(5))
    return SVG.format(w=v.get("w", 660), body=beams + racks + f'<rect x="40" y="540" width="520" height="10" rx="5" fill="var(--good)" opacity=".5" {a(t + .5, "growx", .7)}/>')


def devices(T, v):
    t = T(0)
    icons = [
        # gamepad
        '<rect x="-70" y="-38" width="140" height="76" rx="38" fill="none" stroke="currentColor" stroke-width="10"/><path d="M-40 0h30M-25 -15v30" stroke="currentColor" stroke-width="9" stroke-linecap="round"/><circle cx="30" cy="-8" r="8" fill="currentColor"/><circle cx="46" cy="10" r="8" fill="currentColor"/>',
        # laptop
        '<rect x="-60" y="-50" width="120" height="80" rx="8" fill="none" stroke="currentColor" stroke-width="10"/><path d="M-80 46h160" stroke="currentColor" stroke-width="10" stroke-linecap="round"/>',
        # car
        '<path d="M-72 18v-22l22-34h96l26 34v22z" fill="none" stroke="currentColor" stroke-width="10" stroke-linejoin="round"/><circle cx="-40" cy="26" r="14" fill="currentColor"/><circle cx="40" cy="26" r="14" fill="currentColor"/>',
        # robot
        '<rect x="-50" y="-36" width="100" height="78" rx="18" fill="none" stroke="currentColor" stroke-width="10"/><circle cx="-20" cy="0" r="10" fill="currentColor"/><circle cx="20" cy="0" r="10" fill="currentColor"/><path d="M0 -36v-22" stroke="currentColor" stroke-width="9"/><circle cx="0" cy="-64" r="9" fill="currentColor"/>',
    ]
    out = ""
    for i, ic in enumerate(icons):
        x, y = (170 if i % 2 == 0 else 430), (180 if i < 2 else 420)
        out += f'<g transform="translate({x} {y})"><g {a(t + .15 + i * .22, "pop", .5)}><g {loop("float", .3 + i * .05, 7, ph=i * .25)} style="color:var(--mut)"><rect x="-110" y="-95" width="220" height="190" rx="36" fill="var(--card2)" stroke="var(--edge)" stroke-width="3"/>{ic}</g></g></g>'
    return SVG.format(w=v.get("w", 620), body=out)


def cash(T, v):
    t = T(0)
    stack = "".join(f'<g {a(t + .1 + i * .07, "down", .4)}><rect x="160" y="{470 - i * 34}" width="280" height="30" rx="6" fill="var(--good)" opacity="{.55 + (i % 2) * .25}"/><rect x="180" y="{478 - i * 34}" width="240" height="14" rx="7" fill="none" stroke="var(--bg)" stroke-width="3" opacity=".5"/></g>' for i in range(9))
    coins = "".join(f'<g {loop("fall", .45 + (i % 3) * .12, ph=i * .17, extra="data-range=\"520\"")}><circle cx="{90 + i * 60}" cy="-40" r="22" fill="var(--good)" stroke="var(--bg)" stroke-width="4"/><text x="{90 + i * 60}" y="-30" text-anchor="middle" font-family="Anton" font-size="26" fill="var(--bg)">$</text></g>' for i in range(8))
    return SVG.format(w=v.get("w", 620), body=f'<g opacity=".9">{coins}</g>{stack}')


def globe(T, v):
    t = T(0)
    lock = v.get("lock", False)
    mer = "".join(f'<ellipse cx="300" cy="300" rx="{rx}" ry="200" fill="none" stroke="var(--good)" stroke-width="3" opacity=".55"/>' for rx in (200, 150, 90, 30))
    lat = "".join(f'<ellipse cx="300" cy="{300 + dy}" rx="{(200 ** 2 - dy ** 2) ** .5:.0f}" ry="{18 - abs(dy) / 12:.0f}" fill="none" stroke="var(--good)" stroke-width="3" opacity=".4"/>' for dy in (-140, -70, 0, 70, 140))
    pins = ""
    for i, (x, y, tn) in enumerate(v.get("pins", [])):
        pins += f'<g {a(T(v.get("pin_at", 0)) + .2 + i * .08, "pop", .4)}><circle cx="{x}" cy="{y}" r="13" fill="var(--{tn})" stroke="var(--bg)" stroke-width="4"/><circle cx="{x}" cy="{y}" r="13" fill="none" stroke="var(--{tn})" stroke-width="3" {loop("pulse", .8, .6, ph=i * .13)}/></g>'
    lk = ""
    if lock:
        lt = T(v.get("lock_at", 1))
        lk = f'<g {a(lt, "stamp", .55, "data-rot='0'")}><rect x="215" y="260" width="170" height="140" rx="22" fill="var(--bad)"/><path d="M245 262v-40a55 55 0 0 1 110 0v40" fill="none" stroke="var(--bad)" stroke-width="22"/><circle cx="300" cy="320" r="16" fill="var(--bg)"/><rect x="292" y="320" width="16" height="44" rx="6" fill="var(--bg)"/></g>'
    return SVG.format(w=v.get("w", 600), body=f"""<g {a(t, "zoom", .7)}><circle cx="300" cy="300" r="250" fill="var(--good)" opacity=".08" {loop("glow", .4)}/>
<circle cx="300" cy="300" r="200" fill="var(--card2)" stroke="var(--good)" stroke-width="5"/>
<g {loop("spin", .03, extra='style="transform-box:view-box;transform-origin:300px 300px"')}>{mer}</g>{lat}
<ellipse cx="300" cy="300" rx="290" ry="70" fill="none" stroke="var(--mut)" stroke-width="2" stroke-dasharray="6 12" opacity=".6" transform="rotate(-18 300 300)"/>
{pins}{lk}</g>""")


def bucket(T, v):
    t = T(0)
    stripes = "".join(f'<path d="M{165 + i * 54} 250 L{190 + i * 44} 540 L{212 + i * 44} 540 L{192 + i * 54} 250Z" fill="var(--bad)"/>' for i in range(5))
    legs = ""
    for i, (x, r) in enumerate([(220, -18), (300, 4), (380, 22)]):
        legs += f'<g {a(t + .35 + i * .12, "up", .5)}><g transform="rotate({r} {x} 250)"><ellipse cx="{x}" cy="190" rx="52" ry="70" fill="#c9852f"/><ellipse cx="{x - 12}" cy="170" rx="22" ry="30" fill="#e3a24c" opacity=".7"/><rect x="{x - 9}" y="240" width="18" height="40" fill="#f1e4cc"/></g></g>'
    steam = "".join(f'<path d="M{230 + i * 70} 110 q-18 -30 0 -60 q18 -30 0 -60" fill="none" stroke="var(--mut)" stroke-width="7" stroke-linecap="round" opacity=".5" {loop("rise", .35, ph=i * .3, extra="data-range='70'")}/>' for i in range(3))
    return SVG.format(w=v.get("w", 560), body=f"""{steam}{legs}<g {a(t, "up", .55)}>
<path d="M140 240 H460 L425 545 H175 Z" fill="#fbf6ee"/>{stripes}
<rect x="128" y="228" width="344" height="34" rx="12" fill="#fbf6ee" stroke="var(--bad)" stroke-width="5"/></g>""")


def store(T, v):
    t, tc = T(0), T(v.get("close_at", "+1.0"))
    aw = "".join(f'<path d="M{70 + i * 66} 150 h66 v70 a33 33 0 0 1 -66 0z" fill="{"var(--bad)" if i % 2 == 0 else "#fbf6ee"}"/>' for i in range(7))
    return SVG.format(w=v.get("w", 640), body=f"""<g {a(t, "up", .55)}>
<rect x="70" y="190" width="462" height="350" rx="8" fill="var(--card2)" stroke="var(--edge)" stroke-width="4"/>
<rect x="60" y="120" width="482" height="36" rx="8" fill="var(--mut)"/>{aw}
<rect x="110" y="290" width="200" height="190" rx="8" fill="#9cc8ff" opacity=".35"/>
<rect x="350" y="290" width="140" height="250" rx="6" fill="var(--mut)" opacity=".55"/>
<g style="transform-box:view-box;transform-origin:300px 270px" data-at="{tc:.3f}" data-anim="growy" data-dur="1.1"><rect x="96" y="270" width="410" height="270" fill="#585e6b"/>
{''.join(f'<rect x="96" y="{280 + i * 26}" width="410" height="4" fill="#3d424c"/>' for i in range(10))}</g>
<g {a(tc + .9, "stamp", .5, 'data-rot="-8"')}><rect x="180" y="355" width="240" height="90" rx="14" fill="var(--bad)"/><text x="300" y="420" text-anchor="middle" font-family="Anton" font-size="62" fill="#fff">CLOSED</text></g>
</g>""")


def document(T, v):
    t = T(0)
    lines = "".join(f'<rect x="170" y="{230 + i * 40}" width="{260 - (i % 3) * 50}" height="14" rx="7" fill="var(--mut)" opacity=".5" {a(t + .3 + i * .07, "growx", .5, "style='transform-box:view-box;transform-origin:170px 0'")}/>' for i in range(7))
    st = v.get("doc_stamp", "")
    stamp = f'<g {a(T(v.get("stamp_at", "+1.2")), "stamp", .5, "data-rot='-14'")}><rect x="150" y="380" width="300" height="100" rx="12" fill="none" stroke="var(--bad)" stroke-width="10"/><text x="300" y="452" text-anchor="middle" font-family="Anton" font-size="{v.get("stamp_size", 60)}" fill="var(--bad)">{st}</text></g>' if st else ""
    gav = ""
    if v.get("gavel"):
        gt = T(v.get("gavel_at", "+0.8"))
        gav = f'<g style="transform-box:view-box;transform-origin:520px 470px" data-rot="-28" data-rfrom="-70" data-rat="{gt:.3f}" data-rdur=".35"><rect x="400" y="170" width="150" height="70" rx="16" fill="#8a5a33"/><rect x="465" y="230" width="22" height="240" rx="10" fill="#6d4526"/></g>'
    return SVG.format(w=v.get("w", 600), body=f"""<g {a(t, "up", .55)}><g {loop("float", .2, 6)}>
<rect x="130" y="110" width="340" height="430" rx="22" fill="var(--card2)" stroke="var(--edge)" stroke-width="4"/>
<text x="170" y="190" font-family="Anton" font-size="44" fill="var(--ink)">{v.get("doc_title", "")}</text>{lines}{stamp}</g></g>{gav}""")


def rocket(T, v):
    t = T(0)
    stars = "".join(f'<rect x="{(i * 137) % 600}" y="-40" width="4" height="{40 + (i % 3) * 30}" rx="2" fill="var(--ink)" opacity=".35" {loop("fall", .9 + (i % 4) * .3, ph=(i * .37) % 1, extra="data-range='700'")}/>' for i in range(14))
    smoke = "".join(f'<circle cx="{300 + ((i * 47) % 60) - 30}" cy="470" r="{20 + (i % 4) * 8}" fill="var(--mut)" opacity=".5" {loop("fall", .9, ph=i * .11, extra="data-range='220' data-dx='" + str(((i * 53) % 120) - 60) + "'")}/>' for i in range(9))
    return SVG.format(w=v.get("w", 600), body=f"""{stars}<g {a(t, "up", .8)}><g {loop("float", .9, 6)}>{smoke}
<g style="transform-origin:300px 440px" {loop("flicker", 1, .25)}><path d="M270 430 Q300 560 330 430Z" fill="#ffb02e"/><path d="M285 430 Q300 510 315 430Z" fill="#fff3c4"/></g>
<path d="M300 70 C350 130 360 220 352 430 H248 C240 220 250 130 300 70Z" fill="#f1f3f7"/>
<path d="M300 70 C330 104 342 140 348 170 H252 C258 140 270 104 300 70Z" fill="var(--bad)"/>
<circle cx="300" cy="250" r="30" fill="#2b3a55" stroke="var(--mut)" stroke-width="7"/>
<path d="M250 350 L200 450 H250Z M350 350 L400 450 H350Z" fill="var(--bad)"/></g></g>""")


def orbit(T, v):
    t = T(0)
    sats = ""
    for i in range(5):
        sats += (f'<g {loop("spin", .05 + i * .006, ph=i * .2, extra="style='transform-box:view-box;transform-origin:300px 560px'")}>'
                 f'<g transform="translate(300 {300 - i * 34})"><rect x="-12" y="-9" width="24" height="18" rx="3" fill="var(--ink)"/><rect x="-42" y="-6" width="26" height="12" fill="var(--good)"/><rect x="16" y="-6" width="26" height="12" fill="var(--good)"/></g></g>')
    waves = "".join(f'<path d="M{430 - i * 0} {400 + i * 0} m-{30 + i * 26} 0 a{30 + i * 26} {30 + i * 26} 0 0 1 {60 + i * 52} 0" fill="none" stroke="var(--good)" stroke-width="6" stroke-linecap="round" {loop("glow", 1.2, ph=-i * .25)}/>' for i in range(3))
    return SVG.format(w=v.get("w", 640), body=f"""<defs><clipPath id="oc"><rect x="-200" y="-200" width="1000" height="800"/></clipPath></defs><g clip-path="url(#oc)"><g {a(t, "zoom", .8)}>
<circle cx="300" cy="900" r="520" fill="#1d4ed8" opacity=".85"/><circle cx="300" cy="900" r="520" fill="none" stroke="var(--good)" stroke-width="4" opacity=".6"/>
<path d="M60 560 q120 -60 240 -20 q120 40 240 -10" fill="#22c55e" opacity=".35"/>
{sats}
<g transform="translate(0 30)"><g {a(t + .6, "pop", .5)}>{waves}<path d="M398 520 h64 l-16 -40 h-32z" fill="var(--mut)"/><rect x="410" y="440" width="40" height="44" rx="6" fill="var(--ink)"/></g></g>
</g></g>""")


def people(T, v):
    t = T(0)
    out = ""
    n = v.get("n", 36)
    for i in range(n):
        x, y = 90 + (i % 6) * 84, 70 + (i // 6) * 84
        tn = "good" if i >= v.get("old", 0) else "mut"
        at = T(v.get("grow_at", 0)) + (i * .045 if i < v.get("old", 0) else .6 + (i - v.get("old", 0)) * .05)
        out += f'<g {a(at, "pop", .35)} style="color:var(--{tn})"><circle cx="{x}" cy="{y}" r="16" fill="currentColor"/><path d="M{x - 26} {y + 52} a26 26 0 0 1 52 0z" fill="currentColor"/></g>'
    return SVG.format(w=v.get("w", 560), body=out)


def burn(T, v):
    t = T(0)
    fl = "".join(f'<g style="transform-origin:{230 + i * 70}px 330px" {loop("flicker", .8 + i * .15, .35, ph=i * .3)}><path d="M{200 + i * 70} 330 q30 -120 30 -150 q30 70 30 150z" fill="{["#ff6a1a", "#ffb02e", "#ff4d5e"][i % 3]}" opacity=".9"/></g>' for i in range(4))
    return SVG.format(w=v.get("w", 560), body=f"""<g {a(t, "up", .6)}><g transform="rotate(-8 300 380)">
<rect x="130" y="320" width="340" height="170" rx="18" fill="var(--good)" opacity=".85"/><circle cx="300" cy="405" r="48" fill="none" stroke="var(--bg)" stroke-width="8"/>
<text x="300" y="428" text-anchor="middle" font-family="Anton" font-size="62" fill="var(--bg)">$</text></g>{fl}
{''.join(f'<circle cx="{220 + i * 40}" cy="250" r="6" fill="#ffb02e" {loop("rise", .6, ph=i * .21, extra="data-range='200'")}/>' for i in range(5))}</g>""")


def chart_up(T, v):
    t = T(0)
    return SVG.format(w=v.get("w", 620), body=f"""<g {a(t, "fade", .4)}>{''.join(f'<line x1="60" x2="560" y1="{120 + i * 90}" y2="{120 + i * 90}" stroke="var(--edge)" stroke-width="2"/>' for i in range(5))}
<path d="M60 470 L170 420 L260 440 L360 300 L450 250 L560 90" fill="none" stroke="var(--good)" stroke-width="12" stroke-linejoin="round" stroke-linecap="round" {a(t + .2, "draw", 1.3)}/>
<path d="M520 90 H562 V132" fill="none" stroke="var(--good)" stroke-width="12" stroke-linecap="round" {a(t + 1.4, "pop", .4)}/></g>""")


def cashflow(T, v):
    t = T(0)
    nodes = v.get("nodes", [("$", "good"), ("↑", "mut"), ("AI", "bad")])
    out = ""
    pos = [(300, 90), (130, 450), (470, 450)]
    out += f'<path d="M300 150 L150 400 M300 150 L450 400" stroke="var(--good)" stroke-width="6" stroke-dasharray="14 14" fill="none" {a(t + .3, "draw", .8)}/>'
    for i in range(6):
        side = 1 if i % 2 else -1
        out += f'<circle cx="300" cy="150" r="14" fill="var(--good)" {loop("fall", .5, ph=i / 6, extra=f"data-range='250' data-dx='{side * 150}'")}/>'
    for i, ((x, y), (txt, tn)) in enumerate(zip(pos, nodes)):
        out += f'<g {a(t + i * .25, "pop", .5)}><circle cx="{x}" cy="{y}" r="78" fill="var(--card2)" stroke="var(--{tn})" stroke-width="7"/><text x="{x}" y="{y + 24}" text-anchor="middle" font-family="Anton" font-size="66" fill="var(--{tn})">{txt}</text></g>'
    return SVG.format(w=v.get("w", 600), body=out)


ART = dict(gpu=gpu, servers=servers, devices=devices, cash=cash, globe=globe, bucket=bucket, store=store,
           document=document, rocket=rocket, orbit=orbit, people=people, burn=burn, chart_up=chart_up, cashflow=cashflow)
