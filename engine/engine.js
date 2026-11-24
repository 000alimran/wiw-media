// Deterministic timeline engine: window.render(t) sets every element's state from time t (seconds).
(function () {
  const C = x => Math.max(0, Math.min(1, x));
  const Ez = {
    cubic: x => 1 - Math.pow(1 - x, 3),
    quint: x => 1 - Math.pow(1 - x, 5),
    expo: x => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
    back: x => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
    inout: x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  };
  window.Ez = Ez; window.C = C;

  function splitWords(el) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nodes = []; let n; while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(tn => {
      const frag = document.createDocumentFragment();
      tn.textContent.split(/(\s+)/).forEach(part => {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
        const s = document.createElement('span'); s.className = 'w'; s.textContent = part; frag.appendChild(s);
      });
      tn.parentNode.replaceChild(frag, tn);
    });
  }

  function prep() {
    document.querySelectorAll('.say').forEach(el => {
      splitWords(el);
      const at = +el.dataset.at, end = +el.dataset.end;
      const ws = [...el.querySelectorAll('.w')];
      const span = Math.min((end - at) * 0.8, ws.length * 0.24);
      ws.forEach((w, i) => { w.dataset.at = (at + (ws.length > 1 ? i * span / (ws.length - 1) : 0) - 0.08).toFixed(3); w.dataset.anim = 'word'; w.dataset.dur = '0.42'; });
      el.removeAttribute('data-at');
    });
    // Hook frame: inside [data-hook], anything due before the hook time is already fully shown at t=0,
    // so the very first frame (feed preview / grid cover) carries the hook instead of an empty background.
    document.querySelectorAll('[data-at]').forEach(el => {
      el._base = el.dataset.base || '';
      const h = el.closest('[data-hook]');
      el._instant = !!h && +el.dataset.at <= +h.dataset.hook;
    });
    document.querySelectorAll('[data-hook] [data-count]').forEach(el => {
      el._instant = +el.dataset.cat <= +el.closest('[data-hook]').dataset.hook;
    });
    document.querySelectorAll('path[data-anim=draw], line[data-anim=draw], circle[data-anim=draw], polyline[data-anim=draw]').forEach(p => {
      p.setAttribute('pathLength', '1'); p.style.strokeDasharray = '1';
    });
  }

  function fmt(v, dec, sep) {
    let s = v.toFixed(dec);
    if (sep) { const [a, b] = s.split('.'); s = a.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (b ? '.' + b : ''); }
    return s;
  }

  window.render = function (T) {
    let t = T;
    document.querySelectorAll('[data-at]').forEach(el => {
      const d = el.dataset, at = +d.at, dur = +(d.dur || 0.7), anim = d.anim || 'up';
      t = el._instant ? Math.max(T, at + dur) : T;
      const p = C((t - at) / dur);
      let tf = '', op = 1, bl = 0, extra = null;
      if (t < at) op = 0;
      switch (anim) {
        case 'up': { const e = Ez.quint(p); tf = `translateY(${(1 - e) * 80}px)`; op *= C(p * 1.6); bl = (1 - e) * 16; break; }
        case 'down': { const e = Ez.quint(p); tf = `translateY(${-(1 - e) * 80}px)`; op *= C(p * 1.6); bl = (1 - e) * 16; break; }
        case 'word': { const e = Ez.quint(p); tf = `translateY(${(1 - e) * 36}px)`; op *= C(p * 1.8); bl = (1 - e) * 12; break; }
        case 'pop': { const e = Ez.back(p); tf = `scale(${0.55 + 0.45 * e})`; op *= C(p * 2.2); bl = (1 - Ez.cubic(p)) * 10; break; }
        case 'stamp': { const e = Ez.back(p); tf = `scale(${1.9 - 0.9 * e}) rotate(${d.rot || -6}deg)`; op *= C(p * 3); break; }
        case 'left': { const e = Ez.quint(p); tf = `translateX(${-(1 - e) * 140}px)`; op *= C(p * 1.6); bl = (1 - e) * 12; break; }
        case 'right': { const e = Ez.quint(p); tf = `translateX(${(1 - e) * 140}px)`; op *= C(p * 1.6); bl = (1 - e) * 12; break; }
        case 'zoom': { const e = Ez.quint(p); tf = `scale(${1.25 - 0.25 * e})`; op *= C(p * 1.6); bl = (1 - e) * 20; break; }
        case 'fade': op *= Ez.cubic(p); break;
        case 'enter': { const e = Ez.quint(p); tf = `scale(${1.14 - 0.14 * e})`; op *= C(p * 2); bl = (1 - e) * 22; break; }
        case 'sweep': { const e = Ez.inout(p); tf = `translateX(${-1700 + 3400 * e}px) skewX(-18deg)`; op = (t < at || p >= 1) ? 0 : 1; break; }
        case 'cursor': { const e = Ez.inout(p); tf = `translate(${(1 - e) * 280}px,${(1 - e) * 340}px)`; op = t < at ? 0 : C(p * 4); break; }
        case 'press': { const q = C((t - at) / 0.25); tf = `scale(${1 - 0.08 * Math.sin(Math.PI * q)})`; op = 1; break; }
        case 'wipe': { const e = Ez.inout(p); extra = () => { el.style.clipPath = `inset(0 ${(1 - e) * 100}% 0 0)`; }; op = t < at ? 0 : 1; break; }
        case 'growx': { const e = Ez.expo(p); tf = `scaleX(${Math.max(0.0001, e)})`; op = t < at ? 0 : 1; break; }
        case 'growy': { const e = Ez.expo(p); tf = `scaleY(${Math.max(0.0001, e)})`; op = t < at ? 0 : 1; break; }
        case 'draw': { const e = Ez.inout(p); extra = () => { el.style.strokeDashoffset = String(1 - e); }; op = t < at ? 0 : 1; break; }
      }
      if (d.out !== undefined) {
        const q = C((T - +d.out) / +(d.outdur || 0.45)), eo = Ez.inout(q);
        op *= 1 - eo; bl += eo * 14;
        const oy = d.outmode === 'zoom' ? null : -eo * 60;
        tf = (d.outmode === 'zoom' ? `scale(${1 + eo * 0.15}) ` : `translateY(${oy}px) `) + tf;
      }
      if (extra) extra();
      el.style.transform = (el._base + ' ' + tf).trim();
      el.style.opacity = op.toFixed(3);
      el.style.filter = bl > 0.05 ? `blur(${bl.toFixed(2)}px)` : 'none';
    });
    t = T;
    document.querySelectorAll('[data-count]').forEach(el => {
      const d = el.dataset, p = el._instant ? 1 : C((t - +d.cat) / +(d.cdur || 1.6)), e = Ez.expo(p);
      const v = +d.from + (+d.count - +d.from) * e;
      el.textContent = (d.pre || '') + fmt(v, +(d.dec || 0), d.sep !== undefined) + (d.suf || '');
    });
    document.querySelectorAll('[data-rot]').forEach(el => {
      const d = el.dataset, p = C((t - +d.rat) / +(d.rdur || 1.4)), e = Ez.inout(p);
      el.style.transform = `rotate(${+d.rfrom + (+d.rot - +d.rfrom) * e}deg)`;
    });
    document.querySelectorAll('[data-loop]').forEach(el => {
      const d = el.dataset, k = d.loop, ph = +(d.ph || 0), a = +(d.amp || 10), s = +(d.spd || 1);
      const w = Math.sin(2 * Math.PI * (t * s + ph));
      let tf = '', op = null;
      switch (k) {
        case 'float': tf = `translateY(${w * a}px)`; break;
        case 'sway': tf = `rotate(${w * a}deg)`; break;
        case 'spin': tf = `rotate(${(t * s + ph) * 360}deg)`; break;
        case 'pulse': tf = `scale(${1 + (0.5 + 0.5 * w) * a})`; op = 1 - (0.5 + 0.5 * w); break;
        case 'blink': op = 0.25 + 0.75 * C(w * 3 + 0.5); break;
        case 'glow': op = 0.55 + 0.45 * w; break;
        case 'flicker': { const n = Math.sin(t * 29 * s + ph * 7) * 0.6 + Math.sin(t * 13 * s + ph * 3) * 0.4; tf = `scaleY(${1 + n * a}) scaleX(${1 - n * a * 0.3})`; break; }
        case 'fall': case 'rise': {
          const r = +(d.range || 300), q = (((t * s + ph) % 1) + 1) % 1;
          tf = `translate(${(+d.dx || 0) * q}px,${(k === 'fall' ? 1 : -1) * q * r}px)`; op = Math.sin(Math.PI * q); break; }
        case 'drift': { const q = (((t * s + ph) % 1) + 1) % 1; tf = `translate(${w * a}px,${-q * 2100}px)`; op = Math.sin(Math.PI * q) * +(d.op || 0.5); break; }
      }
      el.style.transform = tf; if (op !== null) el.style.opacity = op.toFixed(3);
    });
    document.querySelectorAll('[data-push]').forEach(el => {
      const [a0, a1] = el.dataset.push.split(',').map(Number);
      const q = C((t - a0) / Math.max(0.1, a1 - a0));
      el.style.transform = `scale(${1 + 0.06 * q})`;
    });
    const pr = document.getElementById('prog'); if (pr) pr.style.transform = `scaleX(${C(t / window.TOTAL)})`;
    if (window.ambient) window.ambient(t);
  };

  window.addEventListener('DOMContentLoaded', () => { prep(); window.render(0); window.READY = true; });
})();
