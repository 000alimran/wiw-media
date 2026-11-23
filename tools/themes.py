"""Visual themes. Each video picks one with `theme:` in its spec."""

THEMES = {
    # Dark fintech: near-black, red/mint, grid + glows
    "dark": dict(
        bg="#06080c", ink="#f2f4f7", mut="#7f8898", good="#2ee6a6", bad="#ff4d5e", accent="#2ee6a6",
        card="rgba(255,255,255,.045)", edge="rgba(255,255,255,.1)", logo="#c9de3c",
        display="Anton", num="Inter", body="'Inter Display','Inter',sans-serif", capweight=800,
        em="#2ee6a6", em2="#ff4d5e", emstyle="color", src="#566070",
        background="""<div id="bgA" class="bgfx" style="inset:-200px;background-image:linear-gradient(rgba(255,255,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.06) 1px,transparent 1px);background-size:90px 90px"></div>
<div id="bgB" class="bgfx" style="width:900px;height:900px;border-radius:50%;filter:blur(140px);opacity:.32;background:#ff3b52"></div>
<div id="bgC" class="bgfx" style="width:900px;height:900px;border-radius:50%;filter:blur(140px);opacity:.3;background:#14c98f"></div>
<div class="bgfx" style="inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 40%,rgba(0,0,0,.75) 100%)"></div>""",
        ambient="""A.style.transform=`translate(${(t*6)%90}px,${(t*10)%90}px)`;
B.style.transform=`translate(${-300+Math.sin(t*.35)*120}px,${-250+Math.cos(t*.27)*140}px)`;
Cc.style.transform=`translate(${520+Math.cos(t*.31)*140}px,${1150+Math.sin(t*.23)*160}px)`;""",
    ),
    # Cream editorial: paper, serif numbers, blue/orange
    "cream": dict(
        bg="#f3ede2", ink="#17161a", mut="#8b8375", good="#2747ff", bad="#ff6a1a", accent="#2747ff",
        card="#fffaf1", edge="rgba(23,22,26,.07)", logo="#3c4a0c",
        display="Gelasio", num="Gelasio", body="'DM Sans',sans-serif", capweight=700,
        em="rgba(39,71,255,.28)", em2="rgba(255,106,26,.45)", emstyle="marker", src="#a59d8e",
        background="""<div id="bgB" class="bgfx" style="width:760px;height:760px;border-radius:50%;filter:blur(120px);opacity:.55;background:#ffb98f"></div>
<div id="bgC" class="bgfx" style="width:820px;height:820px;border-radius:50%;filter:blur(120px);opacity:.5;background:#a9b6ff"></div>
<div id="bgA" class="bgfx" style="left:540px;top:760px;width:1300px;height:1300px;margin:-650px 0 0 -650px;border-radius:50%;border:3px dashed rgba(23,22,26,.08)"></div>""",
        ambient="""A.style.transform=`rotate(${t*4}deg)`;
B.style.transform=`translate(${-200+Math.sin(t*.3)*160}px,${-120+Math.cos(t*.22)*140}px)`;
Cc.style.transform=`translate(${480+Math.cos(t*.27)*150}px,${1180+Math.sin(t*.2)*160}px)`;""",
    ),
    # Violet SaaS: gradient, glass cards, lime/pink
    "violet": dict(
        bg="#12052b", ink="#f4efff", mut="#a395c9", good="#c6ff3d", bad="#ff4fd8", accent="#c6ff3d",
        card="rgba(255,255,255,.07)", edge="rgba(255,255,255,.14)", logo="#c6ff3d",
        display="'Archivo Black'", num="'Archivo Black'", body="Inter,sans-serif", capweight=800,
        em="#c6ff3d", em2="#ff4fd8", emstyle="color", src="#6f6496",
        background="""<div class="bgfx" style="inset:0;background:linear-gradient(160deg,#1a0740 0%,#12052b 45%,#0b0320 100%)"></div>
<div id="bgB" class="bgfx" style="width:700px;height:700px;border-radius:50%;filter:blur(110px);opacity:.55;background:#7b2cff"></div>
<div id="bgC" class="bgfx" style="width:620px;height:620px;border-radius:50%;filter:blur(110px);opacity:.32;background:#ff3fc8"></div>
<div id="bgA" class="bgfx" style="inset:-100px;background-image:radial-gradient(rgba(255,255,255,.09) 2px,transparent 2px);background-size:46px 46px"></div>""",
        ambient="""A.style.transform=`translate(${(t*5)%46}px,${-(t*8)%46}px)`;
B.style.transform=`translate(${-180+Math.sin(t*.33)*170}px,${-100+Math.cos(t*.25)*150}px)`;
Cc.style.transform=`translate(${560+Math.cos(t*.29)*160}px,${640+Math.sin(t*.21)*180}px)`;""",
    ),
}
