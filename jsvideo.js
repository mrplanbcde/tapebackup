/* TapeBackup JS clips: short animated explainers drawn in the page (no video file).
   Each clip is a pure function of time, so play, pause, seek and loop are trivial.
   Markup and data come from scripts/jsvideo.py: .jsv[data-clip] + #jsv-data (numbers) + #jsv-text (words, translated). */
(function () {
  "use strict";
  var C = { acc: "#5b27d6", accd: "#4a1fb0", acc100: "#e6dcfb", acc50: "#f2ecfd", ink: "#161320", ink2: "#39354a", muted: "#6e6a7c", line: "#dedce6", surf: "#f7f6fa", green: "#1f9d6b", amber: "#d98a1c", red: "#d4483b", teal: "#2a8fb8" };
  var W = 1280, H = 560;
  var DISPLAY = "'Space Grotesk','Hanken Grotesk',system-ui,sans-serif", BODY = "'Hanken Grotesk',system-ui,sans-serif", MONO = "'Space Mono',ui-monospace,monospace";
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  function clamp(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  var EA = {
    out: function (t) { return 1 - Math.pow(1 - t, 3); },
    io: function (t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; },
    back: function (t) { var c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); }
  };
  function seg(t, a, b, e) { return (e || EA.out)(clamp((t - a) / (b - a))); }
  function el(tag, css, txt) { var e = document.createElement(tag); e.style.cssText = "position:absolute;" + (css || ""); if (txt != null) e.textContent = txt; return e; }
  function add(st, css, txt) { var e = el("div", css, txt); st.appendChild(e); return e; }
  function put(e, o, x, y, s) { e.style.opacity = o; e.style.transform = "translate(" + (x || 0) + "px," + (y || 0) + "px) scale(" + (s == null ? 1 : s) + ")"; }
  function ph(css, w, h, svg) { var e = el("div", css + ";width:" + w + "px;height:" + h + "px"); e.innerHTML = svg; return e; }

  function cart(label, col, w) {
    var bars = ""; for (var i = 0; i < 4; i++) bars += '<rect x="' + (22 + i * 15) + '" y="62" width="8" height="20" rx="2" fill="#fff" opacity=".35"/>';
    return '<svg viewBox="0 0 100 92" width="' + w + '" height="' + (w * .92) + '"><rect width="100" height="92" rx="9" fill="' + col + '"/><path d="M80 0h11a9 9 0 0 1 9 9v11z" fill="#000" opacity=".18"/><rect x="10" y="12" width="80" height="34" rx="4" fill="#fff"/><rect x="10" y="12" width="80" height="8" rx="3" fill="' + col + '" opacity=".25"/><text x="50" y="40" text-anchor="middle" font-family="Space Mono,monospace" font-size="15" font-weight="700" fill="#161320">' + label + "</text>" + bars + "</svg>";
  }
  function drive(w, col) {
    return '<svg viewBox="0 0 260 70" width="' + w + '" height="' + (w * 70 / 260) + '"><rect width="260" height="70" rx="12" fill="' + (col || C.ink2) + '"/><rect x="16" y="24" width="170" height="20" rx="5" fill="#161320"/><rect x="16" y="52" width="72" height="5" rx="2.5" fill="#fff" opacity=".35"/><circle cx="232" cy="35" r="7" fill="' + C.green + '"/></svg>';
  }
  function check(w, col) {
    return '<svg viewBox="0 0 40 40" width="' + w + '" height="' + w + '"><circle cx="20" cy="20" r="20" fill="' + (col || C.green) + '"/><path d="M11 21l6 6 12-14" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }
  function title(st, T) {
    add(st, "left:64px;top:34px;font:700 38px/1.1 " + DISPLAY + ";color:" + C.ink, T.title);
    if (T.sub) add(st, "left:64px;top:84px;font:400 22px " + BODY + ";color:" + C.muted, T.sub);
  }

  var clips = {};

  /* 1. price per TB by generation */
  clips.prices = function (st, D, T) {
    title(st, T);
    var rows = D.bars.map(function (b, i) {
      var y = 140 + i * 72;
      var row = add(st, "left:0;top:" + y + "px;width:1280px;height:56px", "");
      row.appendChild(el("div", "left:64px;top:8px;font:700 30px " + DISPLAY + ";color:" + C.ink, b.g));
      row.lab = row.firstChild;
      row.appendChild(el("div", "left:210px;top:11px;width:780px;height:34px;border-radius:17px;background:" + C.acc50 + ";box-shadow:inset 0 0 0 2px " + C.line));
      var fill = el("div", "left:210px;top:11px;height:34px;width:0;border-radius:17px;background:#b9a4f0");
      row.appendChild(fill);
      var rg = el("div", "left:1010px;top:10px;font:700 25px " + MONO + ";color:" + C.ink2, T["r" + i]);
      row.appendChild(rg);
      return { row: row, fill: fill, rg: rg, lab: row.lab, w: b.w * 780, y: y };
    });
    var badge = add(st, "padding:7px 16px;border-radius:999px;background:" + C.green + ";color:#fff;font:700 20px " + DISPLAY + ";white-space:nowrap", T.cheap);
    var note = add(st, "left:64px;top:508px;font:600 24px " + DISPLAY + ";color:" + C.ink2, T.note);
    return function (t) {
      rows.forEach(function (r, i) {
        var a = seg(t, .4 + i * .45, 1 + i * .45); put(r.row, a, 0, (1 - a) * 22);
        r.fill.style.width = (r.w * seg(t, .9 + i * .45, 3 + i * .45, EA.io)) + "px";
        var on = t > 6, best = i === D.best;
        r.fill.style.background = on ? (best ? C.acc : "#d6d1e6") : "#b9a4f0";
        r.lab.style.color = on && !best ? C.muted : C.ink;
        r.rg.style.color = on && !best ? C.muted : C.ink;
      });
      var b = rows[D.best], a = seg(t, 6, 6.6, EA.back);
      badge.style.left = (210 + b.w + 18) + "px"; badge.style.top = (b.y + 12) + "px"; put(badge, clamp(a), 0, 0, .7 + .3 * a);
      put(note, seg(t, 8.5, 9.2), 0, (1 - seg(t, 8.5, 9.2)) * 14);
    };
  };

  /* 2. choosing a drive */
  clips.drive = function (st, D, T) {
    title(st, T);
    var steps = [["1", T.s1, D.v1], ["2", T.s2, T.v2], ["3", T.s3, D.v3], ["4", T.s4, T.v4]].map(function (s, i) {
      var y = 150 + i * 94;
      var row = add(st, "left:64px;top:" + y + "px;width:560px;height:78px;border-radius:18px;background:#fff;box-shadow:inset 0 0 0 2px " + C.line, "");
      row.appendChild(el("div", "left:18px;top:19px;width:40px;height:40px;border-radius:50%;background:" + C.acc + ";color:#fff;font:700 22px/40px " + DISPLAY + ";text-align:center", s[0]));
      row.appendChild(el("div", "left:76px;top:10px;font:700 27px " + DISPLAY + ";color:" + C.ink, s[1]));
      row.appendChild(el("div", "left:76px;top:44px;font:400 20px " + BODY + ";color:" + C.muted, s[2]));
      var ok = ph("right:18px;top:20px", 38, 38, check(38)); row.appendChild(ok); row.ok = ok;
      return row;
    });
    var panel = add(st, "left:700px;top:150px;width:516px;height:340px;border-radius:24px;background:" + C.acc50 + ";box-shadow:inset 0 0 0 2px " + C.line, "");
    var dr = ph("left:110px;top:88px", 300, 81, drive(300)); panel.appendChild(dr);
    var ct = ph("left:20px;top:80px", 100, 92, cart(D.gen, C.acc, 100)); panel.appendChild(ct);
    var okp = ph("left:238px;top:20px", 40, 40, check(40)); panel.appendChild(okp);
    var p1 = el("div", "left:30px;top:214px;font:700 25px " + MONO + ";color:" + C.ink, T.pi); panel.appendChild(p1);
    var l1 = el("div", "left:30px;top:250px;font:400 20px " + BODY + ";color:" + C.muted, T.internal); panel.appendChild(l1);
    var p2 = el("div", "left:290px;top:214px;font:700 25px " + MONO + ";color:" + C.ink, T.pe); panel.appendChild(p2);
    var l2 = el("div", "left:290px;top:250px;font:400 20px " + BODY + ";color:" + C.muted, T.external); panel.appendChild(l2);
    return function (t) {
      steps.forEach(function (r, i) {
        var a = seg(t, .7 + i * 1.9, 1.3 + i * 1.9); put(r, a, (1 - a) * -40, 0);
        put(r.ok, seg(t, 1.5 + i * 1.9, 1.9 + i * 1.9, EA.back), 0, 0, seg(t, 1.5 + i * 1.9, 1.9 + i * 1.9, EA.back));
      });
      put(panel, seg(t, .5, 1.1), 0, 0);
      put(dr, seg(t, 5.6, 6.2), 0, 0);
      var m = seg(t, 7.6, 8.8, EA.io); put(ct, seg(t, 5.8, 6.4), m * 110, 0);
      put(okp, seg(t, 9, 9.5, EA.back), 0, 0, seg(t, 9, 9.5, EA.back));
      put(p1, seg(t, 6.4, 7), 0, 0); put(l1, seg(t, 6.4, 7), 0, 0); put(p2, seg(t, 7.2, 7.8), 0, 0); put(l2, seg(t, 7.2, 7.8), 0, 0);
    };
  };

  /* 3. calculator walkthrough */
  clips.calc = function (st, D, T) {
    title(st, T);
    var form = add(st, "left:64px;top:140px;width:560px;height:380px;border-radius:24px;background:#fff;box-shadow:inset 0 0 0 2px " + C.line, "");
    var fields = [[T.l1, "100 TB"], [T.l2, "2"], [T.l3, T.v3], [T.l4, T.v4]].map(function (f, i) {
      var y = 24 + i * 76;
      form.appendChild(el("div", "left:28px;top:" + y + "px;font:600 19px " + BODY + ";color:" + C.muted, f[0]));
      form.appendChild(el("div", "left:28px;top:" + (y + 26) + "px;width:504px;height:36px;border-radius:10px;background:" + C.surf + ";box-shadow:inset 0 0 0 2px " + C.line));
      var v = el("div", "left:42px;top:" + (y + 28) + "px;font:700 24px/32px " + MONO + ";color:" + C.ink, ""); form.appendChild(v);
      return { v: v, s: f[1] };
    });
    var btn = el("div", "left:28px;top:326px;padding:0 24px;height:42px;border-radius:21px;background:" + C.acc + ";color:#fff;font:700 19px/42px " + DISPLAY, T.btn); form.appendChild(btn);
    var res = add(st, "left:690px;top:140px;width:526px;height:380px;border-radius:24px;background:" + C.acc50 + ";box-shadow:inset 0 0 0 2px " + C.line, "");
    res.appendChild(el("div", "left:28px;top:22px;font:600 19px " + BODY + ";color:" + C.muted, T.rec));
    var c = ph("left:28px;top:62px", 110, 101, cart("L9", C.acc, 110)); res.appendChild(c);
    res.appendChild(el("div", "left:160px;top:62px;font:700 56px/1 " + DISPLAY + ";color:" + C.ink, D.gen));
    var cnt = el("div", "left:160px;top:128px;font:700 40px/1 " + DISPLAY + ";color:" + C.acc, "0"); res.appendChild(cnt);
    var cl = el("div", "left:222px;top:140px;font:400 22px " + BODY + ";color:" + C.muted, T.carts); res.appendChild(cl);
    var m1 = el("div", "left:28px;top:220px;width:470px;height:54px;border-radius:14px;background:#fff;box-shadow:inset 0 0 0 2px " + C.line); res.appendChild(m1);
    m1.appendChild(el("div", "left:18px;top:13px;font:400 22px " + BODY + ";color:" + C.muted, T.media));
    m1.appendChild(el("div", "right:18px;top:11px;font:700 26px " + MONO + ";color:" + C.ink, T.m1));
    var m2 = el("div", "left:28px;top:290px;width:470px;height:54px;border-radius:14px;background:#fff;box-shadow:inset 0 0 0 2px " + C.line); res.appendChild(m2);
    m2.appendChild(el("div", "left:18px;top:13px;font:400 22px " + BODY + ";color:" + C.muted, T.drive));
    m2.appendChild(el("div", "right:18px;top:11px;font:700 26px " + MONO + ";color:" + C.ink, T.m2));
    return function (t) {
      var starts = [.5, 2.2, 3.4, 4.6];
      fields.forEach(function (f, i) {
        var n = i === 0 ? Math.round(clamp((t - starts[0]) / 1.1) * f.s.length) : (t >= starts[i] ? f.s.length : 0);
        f.v.textContent = f.s.slice(0, n);
      });
      var press = t > 5.8 && t < 6.1 ? .94 : 1; put(btn, 1, 0, 0, press); btn.style.background = t >= 5.8 ? C.accd : C.acc;
      var a = seg(t, 6.2, 6.9); put(res, a, (1 - a) * 60, 0);
      var n = Math.round(D.n * seg(t, 6.9, 8, EA.io)); cnt.textContent = n;
      put(c, seg(t, 6.6, 7.2, EA.back), 0, 0, seg(t, 6.6, 7.2, EA.back));
      put(m1, seg(t, 8.3, 8.9), 0, (1 - seg(t, 8.3, 8.9)) * 12); put(m2, seg(t, 9.1, 9.7), 0, (1 - seg(t, 9.1, 9.7)) * 12);
    };
  };

  /* 4. LTO-10 30 TB vs 40 TB */
  clips.lto10 = function (st, D, T) {
    title(st, T);
    function block(x, w, tb, col, p, pt, t0) {
      var g = add(st, "left:" + x + "px;top:140px;width:420px;height:380px", "");
      var c = ph("left:0;top:" + (w > 260 ? 8 : 52), w, w * .92, cart("LTO-10", col, w)); g.appendChild(c);
      var big = el("div", "left:0;top:" + (w > 260 ? 292 : 262) + "px;font:700 54px/1 " + DISPLAY + ";color:" + C.ink, tb); g.appendChild(big);
      var pr = el("div", "left:0;top:" + (w > 260 ? 350 : 322) + "px;font:700 28px " + MONO + ";color:" + C.ink2, p); g.appendChild(pr);
      var per = el("div", "left:" + (p.length * 17 + 20) + "px;top:" + (w > 260 ? 357 : 329) + "px;font:400 20px " + BODY + ";color:" + C.muted, pt); g.appendChild(per);
      return { g: g, c: c, big: big, pr: pr, per: per, t0: t0 };
    }
    var a = block(70, 220, "30 TB", C.acc, T.p30, T.t30, .5), b = block(500, 300, "40 TB", C.accd, T.p40, T.t40, 3.6);
    var fh = add(st, "left:930px;top:190px;width:290px;padding:16px 18px;border-radius:16px;background:#fff;box-shadow:inset 0 0 0 2px " + C.line + ";font:700 22px/1.25 " + DISPLAY + ";color:" + C.ink, T.fh);
    var nr = add(st, "left:930px;top:300px;width:290px;padding:16px 18px;border-radius:16px;background:" + C.acc50 + ";box-shadow:inset 0 0 0 2px " + C.line + ";font:700 22px/1.25 " + DISPLAY + ";color:" + C.ink, T.nr);
    return function (t) {
      [a, b].forEach(function (x) {
        var s = seg(t, x.t0, x.t0 + .6, EA.back); put(x.c, clamp(s), 0, (1 - s) * 30, .8 + .2 * s);
        put(x.big, seg(t, x.t0 + .6, x.t0 + 1.1), 0, 0); put(x.pr, seg(t, x.t0 + 1.4, x.t0 + 1.9), 0, 0); put(x.per, seg(t, x.t0 + 2, x.t0 + 2.5), 0, 0);
      });
      put(fh, seg(t, 8.2, 8.8), (1 - seg(t, 8.2, 8.8)) * 40, 0); put(nr, seg(t, 9.4, 10), (1 - seg(t, 9.4, 10)) * 40, 0);
    };
  };

  /* 5. software finder */
  clips.finder = function (st, D, T) {
    title(st, T);
    var rows = [[T.q1, "Veeam", C.acc], [T.q2, "Commvault", C.accd], [T.q3, "Nakivo", C.teal], [T.q4, "Veeam M365", C.ink2]].map(function (r, i) {
      var y = 140 + i * 84;
      var g = add(st, "left:0;top:" + y + "px;width:1280px;height:68px", "");
      g.appendChild(el("div", "left:64px;top:0;width:520px;height:68px;border-radius:18px;background:#fff;box-shadow:inset 0 0 0 2px " + C.line));
      g.appendChild(el("div", "left:90px;top:16px;width:36px;height:36px;border-radius:50%;background:" + C.acc + ";color:#fff;font:700 20px/36px " + DISPLAY + ";text-align:center", String(i + 1)));
      g.appendChild(el("div", "left:144px;top:18px;font:600 26px " + DISPLAY + ";color:" + C.ink, r[0]));
      var ar = el("div", "left:604px;top:32px;height:6px;width:0;border-radius:3px;background:" + C.acc); g.appendChild(ar);
      var tip = el("div", "left:604px;top:22px;width:0;height:0;border-left:16px solid " + C.acc + ";border-top:13px solid transparent;border-bottom:13px solid transparent"); g.appendChild(tip);
      var pill = el("div", "left:790px;top:0;width:420px;height:68px;border-radius:18px;background:" + r[2] + ";color:#fff;font:700 30px/68px " + DISPLAY + ";padding-left:28px;box-sizing:border-box", r[1]); g.appendChild(pill);
      return { g: g, ar: ar, tip: tip, pill: pill };
    });
    var more = add(st, "left:64px;top:496px;padding:11px 22px;border-radius:999px;background:" + C.acc50 + ";box-shadow:inset 0 0 0 2px " + C.acc + ";color:" + C.accd + ";font:700 22px " + DISPLAY + ";white-space:nowrap", T.more);
    return function (t) {
      rows.forEach(function (r, i) {
        var t0 = .7 + i * 2, a = seg(t, t0, t0 + .5); put(r.g, a, 0, (1 - a) * 18);
        var w = 150 * seg(t, t0 + .5, t0 + 1.1, EA.io); r.ar.style.width = w + "px"; r.tip.style.left = (604 + w) + "px"; r.tip.style.opacity = w > 4 ? 1 : 0;
        var p = seg(t, t0 + 1, t0 + 1.5, EA.back); put(r.pill, clamp(p), (1 - p) * 30, 0);
      });
      put(more, seg(t, 9.4, 10), 0, (1 - seg(t, 9.4, 10)) * 12);
    };
  };

  /* player */
  function fmt(s) { s = Math.floor(s); return Math.floor(s / 60) + ":" + ("0" + (s % 60)).slice(-2); }

  function init(root) {
    var dataEl = document.getElementById("jsv-data"), textEl = document.getElementById("jsv-text");
    var build = clips[root.getAttribute("data-clip")];
    if (!build || !dataEl || !textEl) return;
    var D, T;
    try { D = JSON.parse(dataEl.textContent); T = JSON.parse(textEl.textContent); } catch (e) { return; }
    var dur = D.dur || 12, hold = 1.6;
    var box = root.querySelector(".jsv-stage"), cv = document.createElement("div");
    cv.className = "jsv-canvas"; cv.style.cssText = "position:absolute;left:0;top:0;width:" + W + "px;height:" + H + "px;transform-origin:0 0;overflow:hidden;background:" + C.surf;
    box.appendChild(cv);
    var update = build(cv, D, T);
    function fit() { cv.style.transform = "scale(" + (box.clientWidth / W) + ")"; }
    fit(); if (window.ResizeObserver) new ResizeObserver(fit).observe(box); else window.addEventListener("resize", fit);

    root.setAttribute("aria-label", T.title);
    var btn = root.querySelector(".jsv-btn"), track = root.querySelector(".jsv-track"), bar = track.firstElementChild, time = root.querySelector(".jsv-time");
    var t = 0, playing = false, user = false, visible = true, last = 0, raf = 0;
    function draw() {
      update(Math.min(t, dur)); bar.style.width = (Math.min(t, dur) / dur * 100) + "%";
      time.textContent = fmt(Math.min(t, dur)) + " / " + fmt(dur);
      root.classList.toggle("is-playing", playing); btn.setAttribute("aria-label", playing ? T.pause : T.play);
    }
    function tick(now) {
      raf = 0; if (!playing) return;
      t += Math.min(.1, (now - last) / 1000); last = now;
      if (t >= dur + hold) t = 0;
      draw(); raf = requestAnimationFrame(tick);
    }
    function play() { if (playing) return; playing = true; last = performance.now(); if (!raf) raf = requestAnimationFrame(tick); draw(); }
    function pause() { playing = false; draw(); }
    function seek(x) { t = Math.max(0, Math.min(dur, x)); draw(); }
    btn.addEventListener("click", function () { user = true; if (playing) pause(); else { if (t >= dur) t = 0; play(); } });
    track.addEventListener("click", function (e) { var r = track.getBoundingClientRect(); seek((e.clientX - r.left) / r.width * dur); });
    box.addEventListener("click", function () { btn.click(); });
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (en) {
        visible = en[0].isIntersecting;
        if (!visible && playing) { playing = false; root.classList.add("is-offscreen"); }
        else if (visible && !user && !reduce && root.classList.contains("is-offscreen")) { root.classList.remove("is-offscreen"); play(); }
      }, { threshold: .25 }).observe(root);
    }
    root.__jsv = { play: play, pause: pause, seek: seek };
    if (reduce) { user = true; seek(dur - .4); } else { draw(); play(); }
  }

  function boot() { var n = document.querySelectorAll(".jsv[data-clip]"); for (var i = 0; i < n.length; i++) init(n[i]); }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(boot); else boot();
})();
