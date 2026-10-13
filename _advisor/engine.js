/* Shared player for the "which X is best for me" advisors (advisor-builder skill).
   The page sets window.ADVISOR (slug, api, names, domain copy in 5 languages, links)
   and contains the standard markup from page.html.tmpl. The API returns a small JSON
   answer; this file draws it as a 20 to 30 second video on a 1280x720 canvas:
   intro, what matters, the ranked shortlist, the top three picks, side by side,
   next steps. Captions are drawn on the video; browser voice is optional and off. */
(function () {
  "use strict";
  var A = window.ADVISOR || {};
  var W = 1280, H = 720;
  var cv = document.getElementById("cv"), ctx = cv.getContext("2d");
  var FONT = '"SF Pro Display","Segoe UI",system-ui,-apple-system,"PingFang SC","Hiragino Sans","Microsoft YaHei","Noto Sans CJK SC",sans-serif';
  var ACC = A.accent || "#f97316", ACC2 = A.accent2 || "#38bdf8";
  // Inside the main site (A.siteTheme) the video accents follow the light/dark toggle.
  function syncTheme() { if (!A.siteTheme) return; var dark = document.documentElement.classList.contains("dark"); ACC = dark ? "#cfff3d" : "#f97316"; ACC2 = dark ? "#38bdf8" : "#5b8bff"; }
  function hexA(hex, a) { var n = parseInt(hex.slice(1), 16); return "rgba(" + (n >> 16 & 255) + "," + (n >> 8 & 255) + "," + (n & 255) + "," + a + ")"; }
  syncTheme();
  var C = { bg: "#0b1220", panel: "#101b2d", panel2: "#16233a", line: "#243552", text: "#f1f5f9", sub: "#cbd5e1", mute: "#8ea0b8", red: "#f87171", ok: "#4ade80", warn: "#fbbf24" };
  var CJK = /[　-〿぀-ヿ㐀-鿿가-힯＀-￯]/;
  var LANGS = A.langs || ["en", "zh", "de", "ja", "es"];
  var GEN = {
    en: { name: "EN", pause: "Pause", play: "Play", replay: "Replay", voiceOn: "Voice on", voiceOff: "Voice off", download: "Download video", share: "Copy link", examples: "Examples:",
      idle: "Describe your situation above, or pick an example.", translating: "Translating the video…", left: "{n} new answers left today.",
      errLimit: "You have used your new answers for today. The examples still work.", errBusy: "Busy right now, please try again in a minute.", errFail: "Something went wrong. Please try again later.",
      errOffline: "The advisor is offline right now. Try one of the examples.", errShort: "Please describe your situation in 3 to 500 characters.",
      recording: "Recording the video in real time, about {n} seconds…", saved: "Video saved ({ext}, captions included, no voice).", noRecord: "Your browser cannot record the video. Try Chrome, Edge or Safari.", copied: "Link copied: ",
      th: ["#", "Option", "Fit", "Why it fits", "Watch out"], weight: "Weight", scored: "{n} options scored", source: "Scores: {s}", tap: "Tap for full screen", howTitle: "How it works" },
    zh: { name: "中文", pause: "暂停", play: "播放", replay: "重播", voiceOn: "语音开", voiceOff: "语音关", download: "下载视频", share: "复制链接", examples: "示例：",
      idle: "在上方描述你的情况，或选择一个示例。", translating: "正在翻译视频…", left: "今天还可以生成 {n} 个新答案。",
      errLimit: "今天的新答案已用完，示例仍可使用。", errBusy: "当前繁忙，请一分钟后再试。", errFail: "出了点问题，请稍后再试。",
      errOffline: "顾问暂时离线，可以先看示例。", errShort: "请用 3 到 500 个字描述你的情况。",
      recording: "正在实时录制视频，约 {n} 秒…", saved: "视频已保存（{ext}，含字幕，无语音）。", noRecord: "你的浏览器无法录制视频，请使用 Chrome、Edge 或 Safari。", copied: "链接已复制：",
      th: ["#", "方案", "匹配度", "适合的原因", "注意"], weight: "权重", scored: "已评分 {n} 个方案", source: "评分来源：{s}", tap: "点击全屏观看", howTitle: "工作原理" },
    de: { name: "DE", pause: "Pause", play: "Abspielen", replay: "Nochmal", voiceOn: "Stimme an", voiceOff: "Stimme aus", download: "Video herunterladen", share: "Link kopieren", examples: "Beispiele:",
      idle: "Beschreiben Sie oben Ihre Situation oder wählen Sie ein Beispiel.", translating: "Video wird übersetzt…", left: "Heute noch {n} neue Antworten.",
      errLimit: "Ihre neuen Antworten für heute sind aufgebraucht. Die Beispiele funktionieren weiterhin.", errBusy: "Gerade ausgelastet, bitte in einer Minute erneut versuchen.", errFail: "Etwas ist schiefgelaufen. Bitte später erneut versuchen.",
      errOffline: "Der Advisor ist gerade offline. Probieren Sie ein Beispiel.", errShort: "Bitte beschreiben Sie Ihre Situation in 3 bis 500 Zeichen.",
      recording: "Das Video wird in Echtzeit aufgenommen, etwa {n} Sekunden…", saved: "Video gespeichert ({ext}, mit Untertiteln, ohne Stimme).", noRecord: "Ihr Browser kann das Video nicht aufnehmen. Versuchen Sie Chrome, Edge oder Safari.", copied: "Link kopiert: ",
      th: ["#", "Option", "Passung", "Warum sie passt", "Achtung"], weight: "Gewicht", scored: "{n} Optionen bewertet", source: "Bewertung: {s}", tap: "Tippen für Vollbild", howTitle: "So funktioniert es" },
    ja: { name: "日本語", pause: "一時停止", play: "再生", replay: "もう一度", voiceOn: "音声オン", voiceOff: "音声オフ", download: "動画をダウンロード", share: "リンクをコピー", examples: "例：",
      idle: "上で状況を入力するか、例を選んでください。", translating: "動画を翻訳中…", left: "本日あと {n} 件の新しい回答を作成できます。",
      errLimit: "本日の新しい回答を使い切りました。例は引き続き利用できます。", errBusy: "混み合っています。1 分ほどしてからもう一度お試しください。", errFail: "問題が発生しました。しばらくしてからもう一度お試しください。",
      errOffline: "アドバイザーは現在オフラインです。例をお試しください。", errShort: "状況を 3〜500 文字で入力してください。",
      recording: "動画をリアルタイムで録画中です（約 {n} 秒）…", saved: "動画を保存しました（{ext}、字幕付き、音声なし）。", noRecord: "このブラウザでは動画を録画できません。Chrome、Edge、Safari をお試しください。", copied: "リンクをコピーしました：",
      th: ["#", "候補", "適合度", "合う理由", "注意点"], weight: "重み", scored: "{n} 件の候補を評価", source: "評価：{s}", tap: "タップで全画面", howTitle: "仕組み" },
    fr: { name: "FR", pause: "Pause", play: "Lire", replay: "Revoir", voiceOn: "Voix activée", voiceOff: "Voix désactivée", download: "Télécharger la vidéo", share: "Copier le lien", examples: "Exemples :",
      idle: "Décrivez votre situation ci-dessus ou choisissez un exemple.", translating: "Traduction de la vidéo…", left: "Encore {n} nouvelles réponses aujourd'hui.",
      errLimit: "Vous avez utilisé vos nouvelles réponses du jour. Les exemples restent disponibles.", errBusy: "Trop de demandes, réessayez dans une minute.", errFail: "Un problème est survenu. Réessayez plus tard.",
      errOffline: "Le conseiller est hors ligne. Essayez un exemple.", errShort: "Décrivez votre situation en 3 à 500 caractères.",
      recording: "Enregistrement de la vidéo en temps réel, environ {n} secondes…", saved: "Vidéo enregistrée ({ext}, sous-titres inclus, sans voix).", noRecord: "Votre navigateur ne peut pas enregistrer la vidéo. Essayez Chrome, Edge ou Safari.", copied: "Lien copié : ",
      th: ["#", "Option", "Adéquation", "Pourquoi elle convient", "Attention"], weight: "Poids", scored: "{n} options évaluées", source: "Notes : {s}", tap: "Touchez pour le plein écran", howTitle: "Comment ça marche" },
    it: { name: "IT", pause: "Pausa", play: "Riproduci", replay: "Rivedi", voiceOn: "Voce attiva", voiceOff: "Voce disattivata", download: "Scarica il video", share: "Copia il link", examples: "Esempi:",
      idle: "Descrivi la tua situazione qui sopra o scegli un esempio.", translating: "Traduzione del video…", left: "Oggi ti restano {n} nuove risposte.",
      errLimit: "Hai usato le nuove risposte di oggi. Gli esempi funzionano ancora.", errBusy: "Troppe richieste, riprova tra un minuto.", errFail: "Qualcosa è andato storto. Riprova più tardi.",
      errOffline: "Il consulente non è disponibile ora. Prova un esempio.", errShort: "Descrivi la tua situazione in 3 a 500 caratteri.",
      recording: "Registrazione del video in tempo reale, circa {n} secondi…", saved: "Video salvato ({ext}, con sottotitoli, senza voce).", noRecord: "Il tuo browser non può registrare il video. Prova Chrome, Edge o Safari.", copied: "Link copiato: ",
      th: ["#", "Opzione", "Adattamento", "Perché è adatta", "Attenzione"], weight: "Peso", scored: "{n} opzioni valutate", source: "Punteggi: {s}", tap: "Tocca per lo schermo intero", howTitle: "Come funziona" },
    nl: { name: "NL", pause: "Pauze", play: "Afspelen", replay: "Opnieuw", voiceOn: "Stem aan", voiceOff: "Stem uit", download: "Video downloaden", share: "Link kopiëren", examples: "Voorbeelden:",
      idle: "Beschrijf hierboven uw situatie of kies een voorbeeld.", translating: "De video wordt vertaald…", left: "Nog {n} nieuwe antwoorden vandaag.",
      errLimit: "U hebt uw nieuwe antwoorden voor vandaag gebruikt. De voorbeelden werken nog.", errBusy: "Het is nu druk, probeer het over een minuut opnieuw.", errFail: "Er ging iets mis. Probeer het later opnieuw.",
      errOffline: "De adviseur is nu offline. Probeer een voorbeeld.", errShort: "Beschrijf uw situatie in 3 tot 500 tekens.",
      recording: "De video wordt live opgenomen, ongeveer {n} seconden…", saved: "Video opgeslagen ({ext}, met ondertitels, zonder stem).", noRecord: "Uw browser kan de video niet opnemen. Probeer Chrome, Edge of Safari.", copied: "Link gekopieerd: ",
      th: ["#", "Optie", "Match", "Waarom het past", "Let op"], weight: "Gewicht", scored: "{n} opties beoordeeld", source: "Scores: {s}", tap: "Tik voor volledig scherm", howTitle: "Zo werkt het" },
    pl: { name: "PL", pause: "Pauza", play: "Odtwórz", replay: "Powtórz", voiceOn: "Głos włączony", voiceOff: "Głos wyłączony", download: "Pobierz wideo", share: "Kopiuj link", examples: "Przykłady:",
      idle: "Opisz swoją sytuację powyżej albo wybierz przykład.", translating: "Tłumaczenie wideo…", left: "Pozostało dziś {n} nowych odpowiedzi.",
      errLimit: "Wykorzystano dzisiejsze nowe odpowiedzi. Przykłady nadal działają.", errBusy: "Duże obciążenie, spróbuj ponownie za minutę.", errFail: "Coś poszło nie tak. Spróbuj ponownie później.",
      errOffline: "Doradca jest teraz niedostępny. Wypróbuj przykład.", errShort: "Opisz swoją sytuację w 3 do 500 znaków.",
      recording: "Nagrywanie wideo w czasie rzeczywistym, około {n} sekund…", saved: "Wideo zapisane ({ext}, z napisami, bez głosu).", noRecord: "Twoja przeglądarka nie może nagrać wideo. Spróbuj Chrome, Edge lub Safari.", copied: "Link skopiowany: ",
      th: ["#", "Opcja", "Dopasowanie", "Dlaczego pasuje", "Uwaga"], weight: "Waga", scored: "Oceniono {n} opcji", source: "Oceny: {s}", tap: "Dotknij, aby otworzyć pełny ekran", howTitle: "Jak to działa" },
    es: { name: "ES", pause: "Pausa", play: "Reproducir", replay: "Repetir", voiceOn: "Voz activada", voiceOff: "Voz desactivada", download: "Descargar vídeo", share: "Copiar enlace", examples: "Ejemplos:",
      idle: "Describe tu situación arriba o elige un ejemplo.", translating: "Traduciendo el vídeo…", left: "Te quedan {n} respuestas nuevas hoy.",
      errLimit: "Has usado tus respuestas nuevas de hoy. Los ejemplos siguen funcionando.", errBusy: "Hay mucha demanda, inténtalo de nuevo en un minuto.", errFail: "Algo salió mal. Inténtalo más tarde.",
      errOffline: "El asesor no está disponible ahora. Prueba un ejemplo.", errShort: "Describe tu situación en 3 a 500 caracteres.",
      recording: "Grabando el vídeo en tiempo real, unos {n} segundos…", saved: "Vídeo guardado ({ext}, con subtítulos, sin voz).", noRecord: "Tu navegador no puede grabar el vídeo. Prueba con Chrome, Edge o Safari.", copied: "Enlace copiado: ",
      th: ["#", "Opción", "Encaje", "Por qué encaja", "Ojo con"], weight: "Peso", scored: "{n} opciones evaluadas", source: "Puntuación: {s}", tap: "Toca para pantalla completa", howTitle: "Cómo funciona" }
  };
  var UI = (function () {
    var q = new URLSearchParams(location.search).get("lang"), saved = null;
    try { saved = localStorage.getItem(A.slug + "-lang"); } catch (e) {}
    var nav = (navigator.language || "en").slice(0, 2).toLowerCase();
    return [q, saved, nav].find(function (l) { return l && LANGS.indexOf(l) >= 0; }) || "en";
  })();
  function T(key) {
    var d = (A.i18n && A.i18n[UI]) || {}, g = GEN[UI] || GEN.en;
    if (d[key] !== undefined) return d[key];
    if (g[key] !== undefined) return g[key];
    return (A.i18n && A.i18n.en && A.i18n.en[key] !== undefined) ? A.i18n.en[key] : GEN.en[key];
  }
  function nameOf() { return (A.name && (A.name[S && S.lang] || A.name[UI] || A.name.en)) || "Advisor"; }

  // ---------- drawing helpers ----------
  function rr(x, y, w, h, r) { r = Math.max(0, Math.min(r, w / 2, h / 2)); ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
  function font(size, weight) { ctx.font = (weight || 500) + " " + size + "px " + FONT; }
  function text(s, x, y, size, color, weight, align) { font(size, weight); ctx.fillStyle = color; ctx.textAlign = align || "left"; ctx.textBaseline = "alphabetic"; ctx.fillText(s, x, y); }
  function fit(s, size, weight, maxW) { s = String(s); font(size, weight); if (ctx.measureText(s).width <= maxW) return s; var t = s; while (t.length > 1 && ctx.measureText(t + "…").width > maxW) t = t.slice(0, -1); return t + "…"; }
  function wrap(s, size, weight, maxW) {
    font(size, weight);
    var parts = String(s).match(/[　-〿぀-ヿ㐀-鿿가-힯＀-￯]|[^\s　-〿぀-ヿ㐀-鿿가-힯＀-￯]+|\s+/g) || [];
    var lines = [], cur = "";
    parts.forEach(function (p) { var next = cur + p; if (ctx.measureText(next).width > maxW && cur.trim()) { lines.push(cur.trim()); cur = p.trim() ? p : ""; } else cur = next; });
    if (cur.trim()) lines.push(cur.trim());
    return lines;
  }
  var ease = function (x) { x = Math.max(0, Math.min(1, x)); return 1 - Math.pow(1 - x, 3); };
  var back = function (x) { x = Math.max(0, Math.min(1, x)); var c = 1.70158; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };

  // ---------- criterion icons (48x48 grid) ----------
  function icon(name, cx, cy, size, color) {
    var s = size / 48, x = cx - size / 2, y = cy - size / 2;
    var X = function (v) { return x + v * s; }, Y = function (v) { return y + v * s; };
    ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = Math.max(2, 3 * s); ctx.lineJoin = "round"; ctx.lineCap = "round";
    function line(pts) { ctx.beginPath(); pts.forEach(function (p, i) { ctx[i ? "lineTo" : "moveTo"](X(p[0]), Y(p[1])); }); ctx.stroke(); }
    function circ(a, b, r, fill) { ctx.beginPath(); ctx.arc(X(a), Y(b), r * s, 0, 7); fill ? ctx.fill() : ctx.stroke(); }
    switch (name) {
      case "cost": circ(24, 24, 17); font(22 * s, 900); ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText("$", X(24), Y(25)); break;
      case "performance": ctx.beginPath(); ctx.arc(X(24), Y(30), 17 * s, Math.PI, 0); ctx.stroke(); line([[24, 30], [34, 18]]); circ(24, 30, 3, true); break;
      case "scale": [10, 20, 30].forEach(function (yy, i) { rr(X(8 + i * 3), Y(yy), (32 - i * 6) * s, 8 * s, 2 * s); ctx.stroke(); }); break;
      case "ease": line([[12, 36], [28, 20]]); circ(32, 16, 7); line([[10, 38], [14, 34]]); break;
      case "security": line([[24, 6], [39, 12], [37, 28], [24, 42], [11, 28], [9, 12], [24, 6]]); line([[17, 24], [22, 29], [31, 19]]); break;
      case "support": circ(24, 24, 16); circ(24, 24, 7); line([[13, 13], [19, 19]]); line([[35, 13], [29, 19]]); line([[13, 35], [19, 29]]); line([[35, 35], [29, 29]]); break;
      case "ecosystem": rr(X(8), Y(8), 14 * s, 14 * s, 3 * s); ctx.stroke(); rr(X(26), Y(8), 14 * s, 14 * s, 3 * s); ctx.stroke(); rr(X(8), Y(26), 14 * s, 14 * s, 3 * s); ctx.stroke(); rr(X(26), Y(26), 14 * s, 14 * s, 3 * s); ctx.fill(); break;
      case "open": line([[16, 14], [7, 24], [16, 34]]); line([[32, 14], [41, 24], [32, 34]]); line([[27, 10], [21, 38]]); break;
      case "cloud": ctx.beginPath(); ctx.moveTo(X(12), Y(34)); ctx.bezierCurveTo(X(4), Y(34), X(4), Y(22), X(12), Y(22)); ctx.bezierCurveTo(X(12), Y(12), X(26), Y(9), X(30), Y(18)); ctx.bezierCurveTo(X(38), Y(14), X(46), Y(22), X(40), Y(28)); ctx.bezierCurveTo(X(46), Y(32), X(42), Y(35), X(38), Y(34)); ctx.closePath(); ctx.stroke(); break;
      case "ai": case "gpu": rr(X(12), Y(12), 24 * s, 24 * s, 4 * s); ctx.stroke(); [17, 24, 31].forEach(function (v) { line([[v, 6], [v, 12]]); line([[v, 36], [v, 42]]); line([[6, v], [12, v]]); line([[36, v], [42, v]]); }); font(11 * s, 900); ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(name === "ai" ? "AI" : "GPU", X(24), Y(25)); break;
      case "k8s": ctx.beginPath(); for (var k = 0; k < 7; k++) { var a = -Math.PI / 2 + k * 2 * Math.PI / 7; ctx[k ? "lineTo" : "moveTo"](X(24 + 18 * Math.cos(a)), Y(24 + 18 * Math.sin(a))); } ctx.closePath(); ctx.stroke(); circ(24, 24, 6); break;
      case "dr": ctx.beginPath(); ctx.arc(X(24), Y(24), 15 * s, -0.3, Math.PI - 0.3); ctx.stroke(); ctx.beginPath(); ctx.arc(X(24), Y(24), 15 * s, Math.PI - 0.3 + 0.6, 2 * Math.PI - 0.6); ctx.stroke(); line([[36, 25], [38, 31], [32, 31]]); line([[12, 23], [10, 17], [16, 17]]); break;
      case "migration": line([[8, 18], [38, 18]]); line([[32, 12], [38, 18], [32, 24]]); line([[40, 32], [10, 32]]); line([[16, 26], [10, 32], [16, 38]]); break;
      case "rack": rr(X(12), Y(6), 24 * s, 36 * s, 3 * s); ctx.stroke(); [12, 20, 28].forEach(function (yy) { line([[16, yy + 3], [32, yy + 3]]); }); break;
      case "power": line([[27, 5], [13, 27], [24, 27], [20, 43], [35, 20], [24, 20], [27, 5]]); break;
      case "cooling": line([[24, 6], [24, 42]]); line([[8, 15], [40, 33]]); line([[8, 33], [40, 15]]); break;
      case "network": circ(24, 10, 5); circ(10, 36, 5); circ(38, 36, 5); line([[22, 15], [12, 31]]); line([[26, 15], [36, 31]]); line([[15, 36], [33, 36]]); break;
      case "analytics": line([[8, 40], [40, 40]]); [[12, 28], [21, 18], [30, 24], [39, 10]].forEach(function (p) { line([[p[0] - 2, 40], [p[0] - 2, p[1]]]); }); break;
      case "lockin": rr(X(11), Y(21), 26 * s, 20 * s, 4 * s); ctx.stroke(); ctx.beginPath(); ctx.arc(X(24), Y(21), 8 * s, Math.PI, 0); ctx.stroke(); circ(24, 31, 2.5, true); break;
      case "storage": ctx.beginPath(); ctx.ellipse(X(24), Y(12), 14 * s, 5 * s, 0, 0, 7); ctx.stroke(); line([[10, 12], [10, 36]]); line([[38, 12], [38, 36]]); ctx.beginPath(); ctx.ellipse(X(24), Y(36), 14 * s, 5 * s, 0, 0, Math.PI); ctx.stroke(); ctx.beginPath(); ctx.ellipse(X(24), Y(24), 14 * s, 5 * s, 0, 0, Math.PI); ctx.stroke(); break;
      case "compute": [8, 19, 30].forEach(function (yy) { rr(X(8), Y(yy), 32 * s, 9 * s, 2 * s); ctx.stroke(); circ(14, yy + 4.5, 1.6, true); }); break;
      case "fleet": [[8, 8], [26, 8], [8, 26], [26, 26]].forEach(function (p) { rr(X(p[0]), Y(p[1]), 14 * s, 14 * s, 3 * s); ctx.stroke(); }); break;
      case "automation": circ(24, 24, 7); for (var g = 0; g < 8; g++) { var b = g * Math.PI / 4; line([[24 + 11 * Math.cos(b), 24 + 11 * Math.sin(b)], [24 + 16 * Math.cos(b), 24 + 16 * Math.sin(b)]]); } break;
      case "global": circ(24, 24, 16); ctx.beginPath(); ctx.ellipse(X(24), Y(24), 7 * s, 16 * s, 0, 0, 7); ctx.stroke(); line([[8, 24], [40, 24]]); break;
      case "people": circ(17, 16, 6); circ(32, 18, 5); ctx.beginPath(); ctx.arc(X(17), Y(40), 11 * s, Math.PI, 0); ctx.stroke(); ctx.beginPath(); ctx.arc(X(33), Y(40), 8 * s, Math.PI, 0); ctx.stroke(); break;
      case "time": circ(24, 24, 16); line([[24, 14], [24, 24], [31, 28]]); break;
      case "compliance": rr(X(10), Y(6), 28 * s, 36 * s, 3 * s); ctx.stroke(); line([[16, 16], [32, 16]]); line([[16, 24], [32, 24]]); line([[16, 33], [20, 37], [28, 29]]); break;
      case "server": [8, 19, 30].forEach(function (yy) { rr(X(8), Y(yy), 32 * s, 9 * s, 2 * s); ctx.stroke(); circ(14, yy + 4.5, 1.6, true); line([[22, yy + 4.5], [34, yy + 4.5]]); }); break;
      case "vm_host": rr(X(5), Y(8), 38 * s, 32 * s, 4 * s); ctx.stroke(); [[10, 13], [26, 13], [10, 26], [26, 26]].forEach(function (q) { rr(X(q[0]), Y(q[1]), 12 * s, 9 * s, 2 * s); ctx.globalAlpha = .35; ctx.fill(); ctx.globalAlpha = 1; ctx.stroke(); }); break;
      case "vm": line([[24, 6], [40, 14], [40, 33], [24, 42], [8, 33], [8, 14], [24, 6]]); line([[8, 14], [24, 23], [40, 14]]); line([[24, 23], [24, 42]]); break;
      case "nas": rr(X(9), Y(6), 30 * s, 36 * s, 4 * s); ctx.stroke(); [15, 21, 27, 33].forEach(function (xx) { line([[xx, 12], [xx, 32]]); }); circ(24, 37, 1.8, true); break;
      case "switch": rr(X(4), Y(16), 40 * s, 16 * s, 3 * s); ctx.stroke(); for (var sp = 0; sp < 6; sp++) ctx.fillRect(X(8 + sp * 6), Y(22), 3.4 * s, 4 * s); break;
      case "firewall": rr(X(6), Y(8), 36 * s, 32 * s, 3 * s); ctx.stroke(); line([[6, 19], [42, 19]]); line([[6, 30], [42, 30]]); line([[18, 8], [18, 19]]); line([[30, 19], [30, 30]]); line([[18, 30], [18, 40]]); break;
      case "backup": rr(X(6), Y(8), 36 * s, 32 * s, 4 * s); ctx.stroke(); ctx.beginPath(); ctx.arc(X(24), Y(24), 9 * s, -Math.PI * 0.15, Math.PI * 1.45); ctx.stroke(); line([[27, 13], [32.5, 15.5], [30, 20.5]]); break;
      case "object": ctx.beginPath(); ctx.ellipse(X(24), Y(12), 15 * s, 5 * s, 0, 0, 7); ctx.stroke(); ctx.beginPath(); ctx.moveTo(X(9), Y(12)); ctx.lineTo(X(13), Y(38)); ctx.ellipse(X(24), Y(38), 11 * s, 4 * s, 0, Math.PI, 0, true); ctx.lineTo(X(39), Y(12)); ctx.stroke(); break;
      case "mgmt": rr(X(6), Y(8), 36 * s, 24 * s, 3 * s); ctx.stroke(); line([[18, 40], [30, 40]]); line([[24, 32], [24, 40]]); line([[12, 25], [19, 18], [25, 22], [35, 13]]); break;
      case "users": circ(17, 16, 6); circ(32, 18, 5); ctx.beginPath(); ctx.arc(X(17), Y(40), 11 * s, Math.PI, 0); ctx.stroke(); ctx.beginPath(); ctx.arc(X(33), Y(40), 8 * s, Math.PI, 0); ctx.stroke(); break;
      case "database": ctx.beginPath(); ctx.ellipse(X(24), Y(11), 14 * s, 5 * s, 0, 0, 7); ctx.stroke(); line([[10, 11], [10, 37]]); line([[38, 11], [38, 37]]); ctx.beginPath(); ctx.ellipse(X(24), Y(37), 14 * s, 5 * s, 0, 0, Math.PI); ctx.stroke(); ctx.beginPath(); ctx.ellipse(X(24), Y(24), 14 * s, 5 * s, 0, 0, Math.PI); ctx.stroke(); break;
      case "app": rr(X(6), Y(9), 36 * s, 30 * s, 3 * s); ctx.stroke(); line([[6, 16], [42, 16]]); ctx.globalAlpha = .45; ctx.fillRect(X(11), Y(21), 12 * s, 13 * s); ctx.globalAlpha = 1; [22, 27, 32].forEach(function (yy) { line([[27, yy], [37, yy]]); }); break;
      case "tape": rr(X(5), Y(10), 38 * s, 28 * s, 4 * s); ctx.stroke(); circ(17, 22, 6); circ(31, 22, 6); line([[17, 28], [31, 28]]); line([[11, 34], [37, 34]]); break;
      case "library": rr(X(6), Y(4), 36 * s, 40 * s, 3 * s); ctx.stroke(); [10, 17, 24].forEach(function (yy) { [11, 19, 27].forEach(function (xx) { ctx.fillRect(X(xx), Y(yy), 6 * s, 4 * s); }); }); line([[6, 32], [42, 32]]); rr(X(12), Y(35), 24 * s, 5 * s, 1.5 * s); ctx.stroke(); line([[35, 10], [35, 28]]); break;
      case "sensor": circ(24, 30, 5, true); ctx.beginPath(); ctx.arc(X(24), Y(30), 12 * s, -2.4, -0.7); ctx.stroke(); ctx.beginPath(); ctx.arc(X(24), Y(30), 19 * s, -2.4, -0.7); ctx.stroke(); break;
      default: circ(24, 24, 9, true);
    }
    ctx.restore();
  }
  function check(cx, cy, r, col) { ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.fillStyle = col; ctx.fill(); ctx.strokeStyle = C.bg; ctx.lineWidth = r / 3.5; ctx.lineCap = "round"; ctx.beginPath(); ctx.moveTo(cx - r * 0.45, cy); ctx.lineTo(cx - r * 0.1, cy + r * 0.38); ctx.lineTo(cx + r * 0.5, cy - r * 0.38); ctx.stroke(); ctx.restore(); }
  function warnIcon(cx, cy, r) { ctx.save(); ctx.beginPath(); ctx.moveTo(cx, cy - r); ctx.lineTo(cx + r, cy + r * 0.8); ctx.lineTo(cx - r, cy + r * 0.8); ctx.closePath(); ctx.fillStyle = C.warn; ctx.fill(); text("!", cx, cy + r * 0.6, r * 1.2, C.bg, 900, "center"); ctx.restore(); }

  // ---------- answer -> timeline ----------
  var S = null;
  function speechSeconds(s, cjkRate, latinRate) { s = String(s || ""); var cjk = (s.match(new RegExp(CJK.source, "g")) || []).length; return cjk / (cjkRate || 5.2) + (s.length - cjk) / (latinRate || 16); }
  function build(plan) {
    var scenes = [];
    function add(kind, caption, extra, min, max) { var sc = { kind: kind, caption: caption || "", dur: clamp(speechSeconds(caption) + 0.6, min || 3.2, max || 4.8) }; for (var k in extra) sc[k] = extra[k]; scenes.push(sc); }
    var sol = plan.solution, maxT = sol ? 38 : 30;
    add("intro", plan.title, {}, 2.6, 2.6);
    add("needs", plan.needsCaption, {}, 3.6, 4.8);
    add("board", plan.shortlistCaption, {}, 4.2, 5.2);
    if (plan.picks.length >= 3) add("podium", "", {}, 3.8, 3.8);
    if (sol) {
      add("pick", plan.picks[0].caption, { pick: 0 }, 3.8, 4.8);
      add("topology", sol.topologyCaption, {}, 4.6, 5.6);
      add("stairs", sol.stepsCaption, {}, 3.6 + sol.steps.length * 0.45, 6.2);
      add("notices", sol.noticesCaption, {}, 3.8, 4.8);
    } else {
      for (var i = plan.picks.length - 1; i >= 0; i--) add("pick", plan.picks[i].caption, { pick: i }, 3.6, 4.8);
      add("compare", plan.compareCaption, {}, 3.8, 4.8);
    }
    add("outro", plan.outro, {}, A.cta ? 4.4 : 3.6, 5.2);
    var sum = scenes.reduce(function (a, sc) { return a + sc.dur; }, 0), k2 = sum > maxT ? maxT / sum : sum < 15 ? 15 / sum : 1;
    var t = 0; scenes.forEach(function (sc) { sc.dur = Math.max(2.4, sc.dur * k2); sc.start = t; t += sc.dur; });
    return { plan: plan, scenes: scenes, total: t, lang: (plan.lang || "en").toLowerCase().slice(0, 2), topo: sol ? layoutTopo(sol) : null };
  }
  function layoutTopo(sol) {
    var order = ["second", "cloud", "edge"], present = {};
    sol.nodes.forEach(function (n) { present[n.zone] = true; });
    var right = order.filter(function (z) { return present[z]; });
    var top = 112, bottom = 566, gap = 16, zones = {};
    if (present.main || !right.length) zones.main = { x: 32, y: top, w: right.length ? 700 : 1216, h: bottom - top };
    var rx = zones.main ? 752 : 32, rw = zones.main ? 496 : 1216, rh = (bottom - top - gap * (right.length - 1)) / Math.max(1, right.length);
    right.forEach(function (z, i) { zones[z] = { x: rx, y: top + i * (rh + gap), w: rw, h: rh }; });
    var pos = {};
    Object.keys(zones).forEach(function (z) {
      var list = sol.nodes.filter(function (n) { return n.zone === z || (z === "main" && !zones[n.zone]); }); if (!list.length) return;
      var r = zones[z], inner = { x: r.x + 14, y: r.y + 40, w: r.w - 28, h: r.h - 52 };
      var cols = z === "main" ? (list.length <= 3 ? list.length : Math.ceil(list.length / 2)) : list.length, rows = Math.ceil(list.length / cols);
      var scale = clamp(Math.min(inner.h / rows / 132, inner.w / cols / 168), 0.6, 1.25);
      list.forEach(function (n, i) { var c = i % cols, ri = Math.floor(i / cols), inRow = Math.min(cols, list.length - ri * cols), cw = inner.w / inRow; pos[n.id] = { x: inner.x + cw * (c + 0.5), y: inner.y + inner.h / rows * (ri + 0.5), s: scale, node: n }; });
    });
    return { zones: zones, pos: pos };
  }

  // ---------- render ----------
  function sceneAt(t) { var sc = S.scenes[0]; for (var i = 0; i < S.scenes.length; i++) if (t >= S.scenes[i].start) sc = S.scenes[i]; return sc; }
  function bg() {
    ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "rgba(148,163,184,0.06)"; ctx.lineWidth = 1;
    for (var gx = 0; gx < W; gx += 40) { ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, H); ctx.stroke(); }
    for (var gy = 0; gy < H; gy += 40) { ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(W, gy); ctx.stroke(); }
  }
  function header(sc, local) {
    var plan = S.plan, lab = plan.labels;
    text(fit(plan.title, 30, 800, 760), 34, 54, 30, C.text, 800);
    text(fit(nameOf() + " · " + (A.siteLabel || location.host), 17, 600, 760), 34, 86, 17, C.mute, 600);
    var label = { needs: lab.needs, board: lab.shortlist, compare: lab.compare, outro: lab.next }[sc.kind] || "", col = ACC;
    if (sc.kind === "pick") label = lab.pick + " #" + (sc.pick + 1);
    if (sc.kind === "podium") label = "Top 3";
    var sl = plan.solution && plan.solution.labels;
    if (sl) label = { topology: sl.topology, stairs: sl.steps, notices: sl.notices }[sc.kind] || label;
    if (!label) return;
    ctx.save(); ctx.globalAlpha = ease(local / 0.4);
    font(24, 800); var w = ctx.measureText(label).width + 50, x = W - 34 - w;
    rr(x, 26, w, 46, 14); ctx.fillStyle = C.panel2; ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.stroke();
    ctx.beginPath(); ctx.arc(x + 20, 49, 6, 0, 7); ctx.fillStyle = col; ctx.fill();
    text(label, x + 34, 58, 24, C.text, 800);
    ctx.restore();
  }
  function caption(sc, local) {
    if (!sc.caption) return;
    var a = ease(local / 0.35), size = 30, lines = wrap(sc.caption, size, 650, 1120);
    if (lines.length > 2) { size = 25; lines = wrap(sc.caption, size, 650, 1150).slice(0, 3); }
    ctx.save(); ctx.globalAlpha = a;
    rr(32, 584, W - 64, 112, 18); ctx.fillStyle = "rgba(16,27,45,.96)"; ctx.fill(); ctx.strokeStyle = C.line; ctx.lineWidth = 1.5; ctx.stroke();
    var lh = size * 1.32, y0 = 640 - (lines.length - 1) * lh / 2 + size * 0.36;
    lines.forEach(function (ln, i) { text(ln, W / 2, y0 + i * lh, size, C.text, 650, "center"); });
    ctx.restore();
  }
  function drawIntro(local) {
    var b = S.plan.board, n = b.length + (S.plan.total > b.length ? 1 : 0), cols = Math.min(4, n), rows = Math.ceil(n / cols);
    var cw = 250, ch = 74, gx = 22, gy = 18, x0 = (W - (cols * cw + (cols - 1) * gx)) / 2, y0 = 340 - (rows * ch + (rows - 1) * gy) / 2;
    for (var i = 0; i < n; i++) {
      var a = back((local - 0.15 - i * 0.12) / 0.45); if (a <= 0) continue;
      var x = x0 + (i % cols) * (cw + gx), y = y0 + Math.floor(i / cols) * (ch + gy) + (1 - clamp(a, 0, 1)) * 30;
      ctx.save(); ctx.globalAlpha = clamp(a, 0, 1);
      rr(x, y, cw, ch, 16); ctx.fillStyle = C.panel2; ctx.fill(); ctx.strokeStyle = C.line; ctx.lineWidth = 1.5; ctx.stroke();
      var label = i < b.length ? b[i].name : "+" + (S.plan.total - b.length);
      text(fit(label, 22, 750, cw - 30), x + cw / 2, y + ch / 2 + 8, 22, i < b.length ? C.sub : C.mute, 750, "center");
      ctx.restore();
    }
    var a2 = ease((local - 0.6) / 0.6);
    ctx.save(); ctx.globalAlpha = a2;
    text(GEN[S.lang] ? (GEN[S.lang].scored || GEN.en.scored).replace("{n}", S.plan.total) : GEN.en.scored.replace("{n}", S.plan.total), W / 2, y0 + rows * (ch + gy) + 40, 26, ACC, 800, "center");
    if (S.plan.source) text(fit(S.plan.source.name, 18, 650, 900), W / 2, y0 + rows * (ch + gy) + 72, 18, C.mute, 650, "center");
    ctx.restore();
  }
  function drawNeeds(local) {
    var needs = S.plan.needs, ex = S.plan.excluded || [], left = ex.length ? 60 : 200, w = ex.length ? 680 : 880;
    var rowH = Math.min(84, 400 / Math.max(1, needs.length)), y0 = 130 + (440 - rowH * needs.length) / 2;
    needs.forEach(function (n, i) {
      var a = ease((local - 0.15 - i * 0.2) / 0.45); if (a <= 0) return;
      var y = y0 + i * rowH;
      ctx.save(); ctx.globalAlpha = a;
      rr(left, y, w, rowH - 14, 16); ctx.fillStyle = C.panel2; ctx.fill(); ctx.strokeStyle = n.weight >= 4 ? ACC : C.line; ctx.lineWidth = n.weight >= 4 ? 2 : 1.5; ctx.stroke();
      var cy = y + (rowH - 14) / 2;
      icon(n.icon, left + 40, cy, 38, n.weight >= 4 ? ACC : C.sub);
      text(fit(n.label, 25, 750, w - 360), left + 76, cy + 9, 25, C.text, 750);
      for (var k = 0; k < 5; k++) {
        var on = k < n.weight, fillA = ease((local - 0.4 - i * 0.2 - k * 0.07) / 0.25);
        rr(left + w - 250 + k * 46, cy - 10, 38, 20, 8); ctx.fillStyle = "#1e2b40"; ctx.fill();
        if (on && fillA > 0) { ctx.save(); ctx.globalAlpha = a * fillA; rr(left + w - 250 + k * 46, cy - 10, 38, 20, 8); ctx.fillStyle = n.weight >= 4 ? ACC : ACC2; ctx.fill(); ctx.restore(); }
      }
      ctx.restore();
    });
    if (!ex.length) return;
    var ax = 776, aw = 444, a0 = ease((local - 0.8) / 0.5);
    ctx.save(); ctx.globalAlpha = a0;
    text(S.plan.labels.excluded.toUpperCase(), ax, 150, 17, C.red, 800);
    ex.forEach(function (e, i) {
      var y = 172 + i * 112;
      rr(ax, y, aw, 96, 16); ctx.fillStyle = "rgba(69,10,10,.55)"; ctx.fill(); ctx.strokeStyle = "rgba(248,113,113,.6)"; ctx.lineWidth = 1.5; ctx.stroke();
      var nm = fit(e.name, 23, 800, aw - 40); text(nm, ax + 20, y + 38, 23, "#fecaca", 800);
      font(23, 800); var nw = ctx.measureText(nm).width; ctx.strokeStyle = C.red; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(ax + 16, y + 30); ctx.lineTo(ax + 24 + nw * ease((local - 1.1 - i * 0.25) / 0.4), y + 30); ctx.stroke();
      wrap(e.reason, 18, 600, aw - 40).slice(0, 2).forEach(function (ln, k) { text(ln, ax + 20, y + 64 + k * 22, 18, C.sub, 600); });
    });
    ctx.restore();
  }
  function drawBoard(local) {
    var b = S.plan.board, picks = S.plan.picks.map(function (p) { return p.id; });
    var rowH = Math.min(62, 440 / b.length), y0 = 124 + (450 - rowH * b.length) / 2, bx = 430, bw = 700;
    b.forEach(function (r, i) {
      var a = ease((local - 0.1 - i * 0.1) / 0.4); if (a <= 0) return;
      var y = y0 + i * rowH, cy = y + rowH / 2, rank = picks.indexOf(r.id), col = rank >= 0 ? ACC : r.out ? "#475569" : "#64748b";
      ctx.save(); ctx.globalAlpha = a;
      var nm = fit(r.name, 22, rank >= 0 ? 800 : 650, 300);
      text(nm, bx - 24, cy + 8, 22, r.out ? C.mute : rank >= 0 ? C.text : C.sub, rank >= 0 ? 800 : 650, "right");
      if (r.out) { font(22, 650); var nw = ctx.measureText(nm).width; ctx.strokeStyle = C.red; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(bx - 28 - nw, cy); ctx.lineTo(bx - 20, cy); ctx.stroke(); }
      var g = ease((local - 0.35 - i * 0.12) / 1.1), w = Math.max(6, bw * r.fit / 100 * g);
      rr(bx, cy - 15, bw, 30, 12); ctx.fillStyle = "#14203a"; ctx.fill();
      rr(bx, cy - 15, w, 30, 12); ctx.fillStyle = col; if (rank >= 0) { ctx.shadowColor = ACC; ctx.shadowBlur = 14; } ctx.fill(); ctx.shadowBlur = 0;
      text(String(Math.round(r.fit * g)), bx + w + 12, cy + 8, 22, rank >= 0 ? C.text : C.mute, 850);
      if (rank >= 0 && g > 0.9) { var bxr = 80; ctx.beginPath(); ctx.arc(bxr, cy, 19, 0, 7); ctx.fillStyle = ACC; ctx.fill(); text("#" + (rank + 1), bxr, cy + 7, 17, C.bg, 900, "center"); }
      if (r.out && g > 0.9) text("✕", 80, cy + 8, 22, C.red, 900, "center");
      ctx.restore();
    });
    ctx.save(); ctx.globalAlpha = ease((local - 0.5) / 0.5); text(S.plan.labels.fit + " / 100", bx + bw, y0 - 12, 16, C.mute, 700, "right"); ctx.restore();
  }
  // Top 3 as a podium: #2 left, #1 centre (tallest), #3 right; blocks rise 3, 2, 1.
  function drawPodium(local) {
    var picks = S.plan.picks, base = 640, slots = [{ i: 1, x: 365, h: 250 }, { i: 0, x: 640, h: 340 }, { i: 2, x: 915, h: 175 }], w = 260;
    ctx.save(); ctx.globalAlpha = ease(local / 0.4); ctx.strokeStyle = C.line; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(150, base + 1.5); ctx.lineTo(1130, base + 1.5); ctx.stroke(); ctx.restore();
    var order = { 2: 0, 1: 1, 0: 2 };
    slots.forEach(function (sl) {
      var p = picks[sl.i]; if (!p) return;
      var a = back((local - 0.2 - order[sl.i] * 0.45) / 0.55); if (a <= 0) return;
      var h = sl.h * clamp(a, 0, 1.08), top = base - h, col = sl.i === 0 ? ACC : sl.i === 1 ? ACC2 : "#94a3b8";
      ctx.save();
      rr(sl.x - w / 2, top, w, h, 14); var g = ctx.createLinearGradient(0, top, 0, base); g.addColorStop(0, hexA(col, .55)); g.addColorStop(1, hexA(col, .12)); ctx.fillStyle = g; ctx.fill();
      ctx.strokeStyle = col; ctx.lineWidth = 2.5; ctx.stroke();
      if (h > 70) text(String(sl.i + 1), sl.x, top + Math.min(h - 12, 110), 96, hexA("#ffffff", .9), 900, "center");
      var ta = clamp((a - 0.75) * 4, 0, 1); ctx.globalAlpha = ta;
      var cy = top - 40;
      ctx.beginPath(); ctx.arc(sl.x, cy, 32, 0, 7); ctx.fillStyle = C.panel2; ctx.fill(); ctx.strokeStyle = col; ctx.lineWidth = 3; ctx.stroke();
      text(String(p.fit), sl.x, cy + 10, 28, C.text, 900, "center");
      var fs = sl.i === 0 ? 32 : 26, nl = wrap(p.name, fs, 800, w + 30).slice(0, 2);
      nl.forEach(function (ln, k) { text(ln, sl.x, cy - 50 - (nl.length - 1 - k) * (fs + 6), fs, C.text, 800, "center"); });
      ctx.restore();
    });
    if (local > 1.6) { for (var k = 0; k < 18; k++) { var ang = k * 2.39, rad = 40 + ((local - 1.6) * 120 + k * 9) % 160, y = 300 - 245 - 90 + Math.sin(ang) * rad * 0.6; ctx.globalAlpha = clamp(1 - (rad - 40) / 160, 0, 1) * 0.8; ctx.fillStyle = k % 2 ? ACC : ACC2; ctx.fillRect(640 + Math.cos(ang) * rad, base - 340 - 130 + Math.sin(ang) * rad * 0.5, 7, 7); } ctx.globalAlpha = 1; }
  }
  function gauge(cx, cy, r, frac, value, label, col, a) {
    ctx.save(); ctx.lineCap = "round";
    ctx.lineWidth = 18; ctx.strokeStyle = "#1e2b40"; ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI * 0.75, Math.PI * 2.25); ctx.stroke();
    var end = Math.PI * 0.75 + Math.PI * 1.5 * frac * a;
    ctx.shadowColor = col; ctx.shadowBlur = 18; ctx.strokeStyle = col; ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI * 0.75, end); ctx.stroke();
    ctx.shadowBlur = 0; ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.arc(cx + r * Math.cos(end), cy + r * Math.sin(end), 6, 0, 7); ctx.fill();
    text(String(Math.round(value * a)), cx, cy + 16, 50, C.text, 900, "center");
    text(label, cx, cy + r + 10, 20, col, 800, "center");
    ctx.restore();
  }
  function drawPick(sc, local) {
    var p = S.plan.picks[sc.pick], lab = S.plan.labels, a = ease(local / 0.45);
    ctx.save(); ctx.globalAlpha = a;
    rr(60, 120 + (1 - a) * 30, 1160, 446, 24); ctx.fillStyle = C.panel2; ctx.fill(); ctx.strokeStyle = sc.pick === 0 ? ACC : C.line; ctx.lineWidth = sc.pick === 0 ? 3 : 1.5; ctx.stroke();
    text("#" + (sc.pick + 1), 100, 214, 76, sc.pick === 0 ? ACC : C.mute, 900);
    var nl = wrap(p.name, 42, 850, 640).slice(0, 2);
    nl.forEach(function (ln, k) { text(ln, 230, 186 + k * 48, 42, C.text, 850); });
    var y = 200 + nl.length * 48 + 10;
    text(lab.why.toUpperCase(), 100, y, 16, C.mute, 800);
    p.why.forEach(function (w, i) { var ai = ease((local - 0.5 - i * 0.3) / 0.4); ctx.save(); ctx.globalAlpha = a * ai; check(116, y + 40 + i * 52, 15, C.ok); text(fit(w, 25, 650, 730), 146, y + 49 + i * 52, 25, C.sub, 650); ctx.restore(); });
    var wy = y + 40 + p.why.length * 52 + 26, aw = ease((local - 1.2) / 0.4);
    ctx.save(); ctx.globalAlpha = a * aw; warnIcon(116, wy - 4, 14); text(fit(lab.watch + ": " + p.watch, 22, 600, 760), 146, wy + 4, 22, "#fde68a", 600); ctx.restore();
    ctx.restore();
    gauge(1040, 300, 92, p.fit / 100, p.fit, lab.fit, sc.pick === 0 ? ACC : ACC2, ease((local - 0.3) / 1.0));
  }
  function dots(x, y, score, col, a) {
    for (var k = 0; k < 5; k++) {
      var cx = x + k * 26; ctx.beginPath(); ctx.arc(cx, y, 9, 0, 7); ctx.fillStyle = "#1e2b40"; ctx.fill();
      var f = clamp(score - k, 0, 1) * a; if (f <= 0) continue;
      ctx.save(); ctx.beginPath(); ctx.rect(cx - 9, y - 9, 18 * f, 18); ctx.clip(); ctx.beginPath(); ctx.arc(cx, y, 9, 0, 7); ctx.fillStyle = col; ctx.fill(); ctx.restore();
    }
  }
  function drawCompare(local) {
    var picks = S.plan.picks, needs = S.plan.needs, a = ease(local / 0.4);
    var lx = 60, colW = Math.min(300, 840 / picks.length), cx0 = 1220 - colW * picks.length, rowH = Math.min(64, 330 / (needs.length + 1)), y0 = 150;
    ctx.save(); ctx.globalAlpha = a;
    rr(lx - 20, 120, 1200, 450, 22); ctx.fillStyle = C.panel; ctx.fill(); ctx.strokeStyle = C.line; ctx.lineWidth = 1.5; ctx.stroke();
    picks.forEach(function (p, j) {
      var x = cx0 + j * colW + colW / 2;
      text("#" + (j + 1), x, y0 + 8, 18, j === 0 ? ACC : C.mute, 900, "center");
      wrap(p.name, 21, 800, colW - 24).slice(0, 2).forEach(function (ln, k) { text(ln, x, y0 + 36 + k * 24, 21, C.text, 800, "center"); });
    });
    needs.forEach(function (n, i) {
      var y = y0 + 96 + i * rowH, ai = ease((local - 0.3 - i * 0.15) / 0.4);
      ctx.save(); ctx.globalAlpha = a * ai;
      ctx.strokeStyle = "rgba(148,163,184,.12)"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(lx, y - rowH / 2); ctx.lineTo(1200, y - rowH / 2); ctx.stroke();
      icon(n.icon, lx + 18, y, 28, C.sub);
      text(fit(n.label, 21, 700, cx0 - lx - 90), lx + 44, y + 7, 21, C.sub, 700);
      for (var k = 0; k < n.weight; k++) { ctx.fillStyle = ACC; ctx.globalAlpha = a * ai * 0.8; ctx.fillRect(lx + 44 + k * 9, y + 16, 6, 4); }
      ctx.globalAlpha = a * ai;
      picks.forEach(function (p, j) { var x = cx0 + j * colW + colW / 2 - 52; dots(x, y, p.scores[n.criterion] || 0, j === 0 ? ACC : ACC2, ease((local - 0.5 - i * 0.15) / 0.6)); });
      ctx.restore();
    });
    var fy = y0 + 96 + needs.length * rowH + 4;
    ctx.strokeStyle = C.line; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(lx, fy - rowH / 2 + 6); ctx.lineTo(1200, fy - rowH / 2 + 6); ctx.stroke();
    text(S.plan.labels.fit, lx + 44, fy + 10, 22, C.text, 800);
    picks.forEach(function (p, j) { text(String(p.fit), cx0 + j * colW + colW / 2, fy + 12, 30, j === 0 ? ACC : C.text, 900, "center"); });
    ctx.restore();
  }
  function drawTopology(local) {
    var sol = S.plan.solution, L = S.topo, lab = sol.labels;
    Object.keys(L.zones).forEach(function (z, i) {
      var r = L.zones[z], a = ease((local - i * 0.12) / 0.45); if (a <= 0) return;
      var sug = sol.nodes.filter(function (n) { return n.zone === z; }).every(function (n) { return n.suggested; }) && z !== "main";
      ctx.save(); ctx.globalAlpha = a;
      rr(r.x, r.y, r.w, r.h, 18); ctx.fillStyle = sug ? "rgba(16,27,45,.55)" : C.panel; ctx.fill(); ctx.strokeStyle = z === "main" ? hexA(ACC, .45) : sug ? "#475569" : C.line; ctx.lineWidth = 2; if (sug) ctx.setLineDash([8, 8]); ctx.stroke(); ctx.setLineDash([]);
      var zl = fit(lab[z] || z, 18, 700, r.w - 40).toUpperCase(); text(zl, r.x + 18, r.y + 28, 17, z === "main" ? ACC : C.mute, 700);
      if (z === "main" && sol.sizing) text(fit(sol.sizing, 17, 650, r.w - 60 - ctx.measureText(zl).width), r.x + r.w - 18, r.y + 28, 17, C.sub, 650, "right");
      ctx.restore();
    });
    var chips = [];
    sol.links.forEach(function (l, i) {
      var a = L.pos[l.from], b = L.pos[l.to]; if (!a || !b) return;
      var g = ease((local - 0.9 - i * 0.25) / 0.6); if (g <= 0) return;
      var Q = l._q || (l._q = linkCurve(a, b, L));
      var toSug = b.node.suggested;
      ctx.save(); ctx.strokeStyle = toSug ? "#64748b" : ACC2; ctx.lineWidth = 3; ctx.lineCap = "round"; if (toSug) ctx.setLineDash([4, 9]);
      ctx.beginPath(); for (var k = 0; k <= 30 * g; k++) { var q = Q(k / 30); ctx[k ? "lineTo" : "moveTo"](q.x, q.y); } ctx.stroke(); ctx.setLineDash([]);
      if (g >= 1) for (var j = 0; j < 4; j++) { var pt = Q((local * 0.45 + j / 4) % 1); ctx.beginPath(); ctx.arc(pt.x, pt.y, 4, 0, 7); ctx.fillStyle = toSug ? "#94a3b8" : ACC2; ctx.fill(); }
      if (l.label && g >= 1) chips.push({ m: clearest(Q, L), label: l.label, col: toSug ? "#64748b" : ACC2 });
      ctx.restore();
    });
    var idx = 0;
    Object.keys(L.pos).forEach(function (id) {
      var p = L.pos[id], n = p.node, a = back((local - 0.3 - idx++ * 0.14) / 0.45); if (a <= 0) return;
      var s = p.s * clamp(a, 0, 1.2), w = 150 * s, h = 116 * s, x = p.x, y = p.y;
      ctx.save();
      rr(x - w / 2, y - h / 2, w, h, 16 * s); ctx.fillStyle = n.suggested ? "rgba(22,35,58,.55)" : C.panel2; ctx.fill();
      ctx.lineWidth = n.suggested ? 2 : 1.5; ctx.strokeStyle = n.suggested ? "#64748b" : C.line; if (n.suggested) ctx.setLineDash([7 * s, 6 * s]); ctx.stroke(); ctx.setLineDash([]);
      icon(n.icon, x, y - 18 * s, 48 * s, n.suggested ? "#94a3b8" : "#e2e8f0");
      var nl = wrap(n.label, 16 * s, 650, w - 14); if (nl.length > 2) nl = [nl[0], fit(nl.slice(1).join(" "), 16 * s, 650, w - 14)];
      nl.forEach(function (ln, k) { text(ln, x, y + (nl.length > 1 ? 30 : 40) * s + k * 18 * s, 16 * s, n.suggested ? C.mute : C.sub, 650, "center"); });
      if (n.count > 1) { var tag = "×" + (n.count >= 10000 ? Math.round(n.count / 1000) + "k" : n.count >= 1000 ? (Math.round(n.count / 100) / 10) + "k" : n.count); font(16 * s, 850); var tw = ctx.measureText(tag).width + 16 * s; rr(x + w / 2 - tw + 6 * s, y - h / 2 - 10 * s, tw, 24 * s, 12 * s); ctx.fillStyle = ACC; ctx.fill(); text(tag, x + w / 2 - tw / 2 + 6 * s, y - h / 2 + 7 * s, 16 * s, C.bg, 850, "center"); }
      if (n.suggested) { var st = lab.suggested || "recommended"; font(13 * s, 750); var sw = ctx.measureText(st).width + 16 * s; rr(x - sw / 2, y + h / 2 - 11 * s, sw, 22 * s, 11 * s); ctx.fillStyle = "#334155"; ctx.fill(); text(st, x, y + h / 2 + 4 * s, 13 * s, "#cbd5e1", 750, "center"); }
      ctx.restore();
    });
    chips.forEach(function (c) { font(16, 750); var w = ctx.measureText(c.label).width + 22, cx = clamp(c.m.x, w / 2 + 8, W - w / 2 - 8); ctx.save(); rr(cx - w / 2, c.m.y - 14, w, 28, 14); ctx.fillStyle = "rgba(11,18,32,.94)"; ctx.fill(); ctx.strokeStyle = c.col; ctx.lineWidth = 1.5; ctx.stroke(); text(c.label, cx, c.m.y + 6, 16, C.text, 750, "center"); ctx.restore(); });
  }
  // A quadratic link from a to b that bends around the other nodes (first bend that clears them wins).
  function linkCurve(a, b, L) {
    var others = Object.keys(L.pos).map(function (k) { return L.pos[k]; }).filter(function (o) { return o !== a && o !== b; });
    var dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy) || 1, nx = -dy / len, ny = dx / len, pick = null;
    var bestGap = -1e9;
    [24, 70, -70, 120, -120, 170, -170].forEach(function (bend) {
      if (bestGap > 0) return;
      var p0 = { x: a.x + dx * 0.16, y: a.y + dy * 0.16 }, p2 = { x: b.x - dx * 0.16, y: b.y - dy * 0.16 }, c = { x: (a.x + b.x) / 2 + nx * bend, y: (a.y + b.y) / 2 + ny * bend };
      var q = function (u) { var v = 1 - u; return { x: v * v * p0.x + 2 * v * u * c.x + u * u * p2.x, y: v * v * p0.y + 2 * v * u * c.y + u * u * p2.y }; };
      var gap = 1e9;
      for (var u = 0.05; u <= 0.95; u += 0.05) { var pt = q(u); others.forEach(function (o) { gap = Math.min(gap, Math.max(Math.abs(pt.x - o.x) - 85 * o.s, Math.abs(pt.y - o.y) - 66 * o.s)); }); if (pt.y < 112 || pt.y > 566 || pt.x < 32 || pt.x > 1248) gap = Math.min(gap, -50); }
      if (gap > bestGap) { bestGap = gap; pick = q; }
    });
    return pick;
  }
  function clearest(Q, L) {
    var bestPt = Q(0.5), bestD = -1;
    for (var u = 0.3; u <= 0.701; u += 0.05) { var c = Q(u), d = 1e9; Object.keys(L.pos).forEach(function (k) { var o = L.pos[k]; d = Math.min(d, Math.max(Math.abs(c.x - o.x) - 75 * o.s, Math.abs(c.y - o.y) - 58 * o.s)); }); if (d > bestD) { bestD = d; bestPt = c; } }
    return bestPt;
  }
  function drawStairs(local) {
    var steps = S.plan.solution.steps, n = steps.length, x0 = 50, x1 = 1230, base = 566, topY = 132;
    var first = 178, w = (x1 - x0) / n, rise = (base - topY - first) / Math.max(1, n - 1), per = Math.max(0.45, (S.scenes[sceneIdxOf("stairs")].dur - 1.2) / n);
    steps.forEach(function (st, i) {
      var a = ease((local - 0.2 - i * per) / 0.45); if (a <= 0) return;
      var top = base - first - i * rise, x = x0 + i * w, h = (base - top) * a;
      ctx.save();
      rr(x + 4, base - h, w - 8, h, 14); var g = ctx.createLinearGradient(0, top, 0, base); g.addColorStop(0, i === n - 1 ? hexA(ACC, .35) : "#1a2a44"); g.addColorStop(1, "#111c30"); ctx.fillStyle = g; ctx.fill();
      ctx.strokeStyle = i === n - 1 ? ACC : C.line; ctx.lineWidth = i === n - 1 ? 2.5 : 1.5; ctx.stroke();
      ctx.globalAlpha = clamp((a - 0.6) * 2.5, 0, 1);
      ctx.beginPath(); ctx.arc(x + 30, top + 30, 17, 0, 7); ctx.fillStyle = i === n - 1 ? ACC : ACC2; ctx.fill(); text(String(i + 1), x + 30, top + 37, 19, C.bg, 900, "center");
      var tl = wrap(st.title, 20, 800, w - 30).slice(0, 2); tl.forEach(function (ln, k) { text(ln, x + 16, top + 74 + k * 24, 20, C.text, 800); });
      wrap(st.detail, 16, 550, w - 30).slice(0, 3).forEach(function (ln, k) { text(ln, x + 16, top + 80 + tl.length * 24 + 4 + k * 21, 16, C.sub, 550); });
      ctx.restore();
    });
    var cur = clamp(Math.floor((local - 0.2) / per), 0, n - 1), frac = clamp(((local - 0.2) - cur * per) / 0.35, 0, 1);
    if (local > 0.6) { var px = x0 + cur * w + w - 34, py = base - first - cur * rise - 16 - Math.sin(frac * Math.PI) * 22; ctx.beginPath(); ctx.arc(px, py, 11, 0, 7); ctx.fillStyle = C.ok; ctx.shadowColor = C.ok; ctx.shadowBlur = 16; ctx.fill(); ctx.shadowBlur = 0; }
  }
  function sceneIdxOf(kind) { for (var i = 0; i < S.scenes.length; i++) if (S.scenes[i].kind === kind) return i; return 0; }
  function drawNotices(local) {
    var items = S.plan.solution.notices, n = items.length, cols = n > 2 ? 2 : 1, cw = cols === 2 ? 570 : 900, ch = 150, x0 = (W - (cols * cw + (cols - 1) * 24)) / 2, rows = Math.ceil(n / cols), y0 = 120 + (450 - rows * ch - (rows - 1) * 20) / 2;
    items.forEach(function (it, i) {
      var a = back((local - 0.2 - i * 0.3) / 0.45); if (a <= 0) return;
      var x = x0 + (i % cols) * (cw + 24), y = y0 + Math.floor(i / cols) * (ch + 20);
      ctx.save(); ctx.globalAlpha = clamp(a, 0, 1);
      rr(x, y, cw, ch, 18); ctx.fillStyle = "rgba(66,44,6,.55)"; ctx.fill(); ctx.strokeStyle = "rgba(251,191,36,.6)"; ctx.lineWidth = 2; ctx.stroke();
      warnIcon(x + 40, y + 52, 20);
      wrap(it, 23, 650, cw - 100).slice(0, 4).forEach(function (ln, k) { text(ln, x + 76, y + 48 + k * 30, 23, "#fde68a", 650); });
      ctx.restore();
    });
  }
  function drawOutro(local) {
    var items = S.plan.next, cta = A.cta, x = cta ? 60 : 250, w = cta ? 640 : 780;
    items.forEach(function (it, i) {
      var a = ease((local - 0.2 - i * 0.3) / 0.4); if (a <= 0) return;
      var y = 150 + i * 78;
      ctx.save(); ctx.globalAlpha = a;
      rr(x, y, w, 62, 16); ctx.fillStyle = C.panel2; ctx.fill(); ctx.strokeStyle = C.line; ctx.stroke();
      check(x + 36, y + 31, 15, ACC);
      text(fit(it, 24, 700, w - 90), x + 66, y + 40, 24, C.text, 700);
      ctx.restore();
    });
    if (cta) {
      var a3 = back((local - 0.5 - items.length * 0.2) / 0.5), cx = 740, cy = 150, cww = 480, chh = 300;
      if (a3 > 0) {
        ctx.save(); ctx.globalAlpha = clamp(a3, 0, 1); ctx.translate(cx + cww / 2, cy + chh / 2); ctx.scale(clamp(a3, 0, 1.06), clamp(a3, 0, 1.06)); ctx.translate(-(cx + cww / 2), -(cy + chh / 2));
        rr(cx, cy, cww, chh, 22); ctx.fillStyle = ACC; ctx.shadowColor = ACC; ctx.shadowBlur = 30; ctx.fill(); ctx.shadowBlur = 0;
        icon("people", cx + 56, cy + 62, 54, C.bg);
        wrap(cta.title[S.lang] || cta.title[UI] || cta.title.en, 34, 850, cww - 60).slice(0, 2).forEach(function (ln, k) { text(ln, cx + 30, cy + 140 + k * 40, 34, C.bg, 850); });
        wrap(cta.line[S.lang] || cta.line[UI] || cta.line.en, 20, 600, cww - 60).slice(0, 2).forEach(function (ln, k) { text(ln, cx + 30, cy + 222 + k * 26, 20, "rgba(11,18,32,.82)", 600); });
        text(cta.urlLabel || cta.href.replace(/^https?:\/\//, ""), cx + 30, cy + chh - 24, 20, C.bg, 800);
        ctx.restore();
      }
    } else {
      var a2 = ease((local - 0.6 - items.length * 0.3) / 0.5);
      ctx.save(); ctx.globalAlpha = a2; text(A.siteLabel || location.host + location.pathname, W / 2, 150 + items.length * 78 + 40, 22, ACC, 750, "center"); ctx.restore();
    }
  }
  function render(t) {
    if (!S) return idle();
    var sc = sceneAt(t), local = t - sc.start;
    bg();
    if (sc.kind === "intro") drawIntro(local);
    else if (sc.kind === "needs") drawNeeds(local);
    else if (sc.kind === "board") drawBoard(local);
    else if (sc.kind === "podium") drawPodium(local);
    else if (sc.kind === "pick") drawPick(sc, local);
    else if (sc.kind === "compare") drawCompare(local);
    else if (sc.kind === "topology") drawTopology(local);
    else if (sc.kind === "stairs") drawStairs(local);
    else if (sc.kind === "notices") drawNotices(local);
    else drawOutro(local);
    header(sc, local); caption(sc, local);
    ctx.fillStyle = ACC; ctx.fillRect(0, H - 4, W * t / S.total, 4);
  }
  var idleMsg = "", idleSpin = false;
  function idle() {
    bg();
    text(nameOf(), W / 2, 300, 54, C.text, 800, "center");
    wrap(idleMsg || T("idle"), 28, 600, 1000).forEach(function (ln, i) { text(ln, W / 2, 370 + i * 40, 28, C.sub, 600, "center"); });
    if (idleSpin) { var a = performance.now() / 300; ctx.strokeStyle = ACC; ctx.lineWidth = 6; ctx.lineCap = "round"; ctx.beginPath(); ctx.arc(W / 2, 470, 26, a, a + 4.2); ctx.stroke(); }
    var ics = A.idleIcons || ["compute", "storage", "network", "cloud", "security", "cost", "performance", "support"];
    ics.forEach(function (ic, i) { icon(ic, W / 2 - (ics.length - 1) * 54 + i * 108, 180, 50, i % 2 ? "#0c4a6e" : "#9a3412"); });
    text(A.siteLabel || location.host, W / 2, 680, 20, C.mute, 650, "center");
  }

  // ---------- player ----------
  var t = 0, playing = false, last = 0, sceneIdx = -1, voiceOn = false, recorder = null, alive = true, timers = [], offs = [];
  function on(target, ev, fn) { target.addEventListener(ev, fn); offs.push(function () { target.removeEventListener(ev, fn); }); }
  var $ = function (id) { return document.getElementById(id); };
  var playBtn = $("play"), restartBtn = $("restart"), fillEl = $("fill"), voiceBtn = $("voice");
  function speak(say, dur) {
    if (!voiceOn || recorder || !("speechSynthesis" in window) || !say) return;
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(say), lang = S.plan.lang || "en";
    u.lang = lang; u.rate = clamp(speechSeconds(say, 4.5, 14) / Math.max(1.5, (dur || 4) - 0.35), 1.0, 1.6);
    var v = speechSynthesis.getVoices().filter(function (x) { return x.lang && x.lang.toLowerCase().indexOf(lang.toLowerCase().slice(0, 2)) === 0; });
    if (v.length) u.voice = v.find(function (x) { return /natural|premium|enhanced|google/i.test(x.name); }) || v[0];
    speechSynthesis.speak(u);
  }
  function frame(now) {
    if (!alive) return;
    syncTheme();
    var dt = Math.min(0.1, (now - last) / 1000); last = now;
    if (S && playing) {
      t += dt;
      if (t >= S.total) { t = S.total; playing = false; playBtn.textContent = T("play"); if (recorder) recorder.stop(); }
      var i = S.scenes.indexOf(sceneAt(t));
      if (i !== sceneIdx) { sceneIdx = i; if (playing) speak(S.scenes[i].caption, S.scenes[i].dur - (t - S.scenes[i].start)); }
    }
    render(S ? Math.min(t, S.total - 0.001) : 0);
    if (S) fillEl.style.width = (100 * t / S.total) + "%";
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(function (n) { last = n; frame(n); });
  playBtn.onclick = function () { if (!S) return; if (t >= S.total) t = 0; playing = !playing; if (!playing && "speechSynthesis" in window) speechSynthesis.cancel(); sceneIdx = -1; playBtn.textContent = playing ? T("pause") : T("play"); };
  restartBtn.onclick = function () { if (!S) return; t = 0; sceneIdx = -1; playing = true; playBtn.textContent = T("pause"); };
  $("bar").onclick = function (e) { if (!S) return; var r = this.getBoundingClientRect(); t = clamp((e.clientX - r.left) / r.width, 0, 1) * S.total; sceneIdx = -1; };
  if (!("speechSynthesis" in window)) voiceBtn.style.display = "none";
  voiceBtn.onclick = function () { voiceOn = !voiceOn; voiceBtn.setAttribute("aria-pressed", String(voiceOn)); voiceBtn.textContent = voiceOn ? T("voiceOn") : T("voiceOff"); if (!voiceOn) speechSynthesis.cancel(); else if (S && playing) { var cur = sceneAt(t); speak(cur.caption, cur.dur - (t - cur.start)); } };

  $("dl").onclick = function () {
    if (!S || recorder || !cv.captureStream || !window.MediaRecorder) { setStatus(T("noRecord"), true); return; }
    var types = ["video/mp4;codecs=avc1", "video/mp4", "video/webm;codecs=vp9", "video/webm"], mime = types.find(function (m) { return MediaRecorder.isTypeSupported(m); }) || "";
    var chunks = [], stream = cv.captureStream(30);
    recorder = new MediaRecorder(stream, mime ? { mimeType: mime, videoBitsPerSecond: 6e6 } : undefined);
    recorder.ondataavailable = function (e) { if (e.data.size) chunks.push(e.data); };
    recorder.onstop = function () {
      var type = recorder.mimeType || mime || "video/webm", ext = type.indexOf("mp4") >= 0 ? "mp4" : "webm";
      var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(chunks, { type: type }));
      a.download = A.slug + "-" + (S.plan.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "video") + "." + ext;
      document.body.appendChild(a); a.click(); a.remove(); recorder = null; setStatus(T("saved").replace("{ext}", ext.toUpperCase())); $("dl").disabled = false;
    };
    if ("speechSynthesis" in window) speechSynthesis.cancel();
    $("dl").disabled = true; setStatus(T("recording").replace("{n}", Math.round(S.total)));
    t = 0; sceneIdx = -1; playing = true; playBtn.textContent = T("pause"); recorder.start(250);
  };
  var shareLink = "";
  $("share").onclick = function () { if (!shareLink) return; (navigator.clipboard ? navigator.clipboard.writeText(shareLink) : Promise.reject()).then(function () { setStatus(T("copied") + shareLink); }, function () { setStatus(shareLink); }); };

  // ---------- details under the video ----------
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function details(plan) {
    var lab = plan.labels, el = $("plan");
    var pod = function (i) { var p = plan.picks[i]; if (!p) return ""; return '<div class="pod p' + (i + 1) + '"><div class="pod-card"><div class="pod-fit"><b>' + p.fit + '</b><small>' + esc(lab.fit) + '</small></div><h3>' + (p.url ? '<a href="' + esc(p.url) + '">' + esc(p.name) + '</a>' : esc(p.name)) + '</h3><ul>' + p.why.map(function (w) { return '<li>' + esc(w) + '</li>'; }).join("") + '</ul><p class="pod-watch">' + esc(lab.watch) + ': ' + esc(p.watch) + '</p></div><div class="pod-step"><span>' + (i + 1) + '</span></div></div>'; };
    var podium = '<div class="podium">' + pod(1) + pod(0) + pod(2) + '</div>';
    var needs = plan.needs.map(function (n) { return '<li>' + esc(n.label) + ' <span class="kind">' + esc(T("weight")) + ' ' + n.weight + '/5</span></li>'; }).join("");
    var ex = (plan.excluded || []).map(function (e) { return '<li><b>' + esc(e.name) + '</b>: ' + esc(e.reason) + '</li>'; }).join("");
    var src = plan.source ? '<p class="note">' + esc(T("source").replace("{s}", plan.source.name + " (" + plan.source.edition + ")")) + ' · <a href="' + esc(plan.source.url) + '">' + esc(plan.source.url.replace(/^https?:\/\//, "")) + '</a></p>' : "";
    var links = (A.links || []).map(function (l) { return '<a href="' + esc(l.href) + '">' + esc(l.label[UI] || l.label.en) + '</a>'; }).join("");
    el.innerHTML = '<h2>' + esc(plan.title) + '</h2><p>' + esc(plan.summary) + '</p>' +
      podium +
      '<div class="cols"><div class="box"><h3>' + esc(lab.needs) + '</h3><ul>' + needs + '</ul>' + (ex ? '<h3 style="margin-top:12px">' + esc(lab.excluded) + '</h3><ul>' + ex + '</ul>' : "") + '</div>' +
      '<div class="box"><h3>' + esc(lab.next) + '</h3><ul>' + plan.next.map(function (c) { return '<li>' + esc(c) + '</li>'; }).join("") + '</ul></div></div>' + solHtml(plan) + ctaHtml() + src +
      (links ? '<div class="more">' + links + '</div>' : "");
    el.style.display = "block";
  }

  // ---------- scenario form (workloads with amounts + a few choices) ----------
  var F = A.form || null, formVals = {};
  function L(o) { return o ? (o[UI] || o.en || "") : ""; }
  function readForm() { if (!F) return; document.querySelectorAll("#scenario [data-k]").forEach(function (el) { formVals[el.dataset.k] = el.value; }); }
  function renderForm() {
    var box = $("scenario"); if (!F || !box) return;
    readForm();
    var h = '';
    if (F.workloads && F.workloads.length) {
      h += '<div class="sc-title">' + esc(L(F.workloadsTitle) || "") + '</div><div class="wl">';
      F.workloads.forEach(function (w) { h += '<label class="wl-row"><span>' + esc(L(w.label)) + '</span><input type="number" min="0" max="100000" inputmode="numeric" placeholder="0" data-k="w_' + w.id + '" value="' + esc(formVals["w_" + w.id] || "") + '" /></label>'; });
      h += '</div>';
    }
    if (F.selects && F.selects.length) {
      h += '<div class="sels">';
      F.selects.forEach(function (sel) {
        h += '<label class="sel"><span>' + esc(L(sel.label)) + '</span><select data-k="s_' + sel.id + '"><option value="">–</option>';
        sel.options.forEach(function (o, i) { h += '<option value="' + i + '"' + (String(formVals["s_" + sel.id]) === String(i) ? " selected" : "") + '>' + esc(L(o)) + '</option>'; });
        h += '</select></label>';
      });
      h += '</div>';
    }
    box.innerHTML = h;
  }
  function setForm(v) { formVals = v || {}; var box = $("scenario"); if (box) box.innerHTML = ""; renderForm(); }
  function clearForm() { setForm({}); }
  function packForm(f) { return Object.keys(f || {}).filter(function (k) { return f[k] !== "" && f[k] !== undefined; }).map(function (k) { return k + "=" + f[k]; }).join(";"); }
  function unpackForm(s) { var f = {}; String(s || "").split(";").forEach(function (p) { var i = p.indexOf("="); if (i > 0) f[p.slice(0, i)] = p.slice(i + 1); }); return f; }
  function compose() {
    var free = $("q").value.trim();
    if (!F) return free;
    readForm();
    var parts = [], cj = UI === "zh" || UI === "ja";
    (F.workloads || []).forEach(function (w) { var n = parseInt(formVals["w_" + w.id], 10); if (n > 0) parts.push(L(w.label) + (cj ? "：" : ": ") + n); });
    (F.selects || []).forEach(function (sel) { var v = formVals["s_" + sel.id]; if (v !== undefined && v !== "") parts.push(L(sel.label) + (cj ? "：" : ": ") + L(sel.options[+v])); });
    if (free) parts.push(free);
    return parts.join(cj ? "；" : "; ").slice(0, 780);
  }

  function solHtml(plan) {
    var sol = plan.solution; if (!sol) return "";
    var sl = sol.labels, names = {}; sol.nodes.forEach(function (n) { names[n.id] = n.label; });
    return '<div class="cols"><div class="box"><h3>' + esc(sl.topology) + '</h3><p style="margin:0 0 8px"><b>' + esc(plan.picks[0].name) + '</b> · ' + esc(sol.sizing) + '</p><ul>' +
      sol.nodes.map(function (n) { return '<li>' + esc(n.label) + (n.count > 1 ? ' ×' + n.count.toLocaleString() : '') + ' <small>(' + esc(sl[n.zone] || n.zone) + (n.suggested ? ', ' + esc(sl.suggested) : '') + ')</small></li>'; }).join("") +
      '</ul></div><div class="box"><h3>' + esc(sl.steps) + '</h3><ol style="margin:0;padding-left:20px;line-height:1.7">' + sol.steps.map(function (x) { return '<li><b>' + esc(x.title) + '</b>: ' + esc(x.detail) + '</li>'; }).join("") + '</ol></div></div>' +
      '<div class="box warnbox"><h3>' + esc(sl.notices) + '</h3><ul>' + sol.notices.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join("") + '</ul></div>';
  }
  function ctaHtml() { var c = A.cta; if (!c) return ""; return '<a class="ctabox" href="' + esc(c.href) + '"><b>' + esc(L(c.title)) + '</b><span>' + esc(L(c.line)) + '</span><i>' + esc(L(c.button) || "→") + '</i></a>'; }

  // ---------- interface language ----------
  var CUR = null, TR = {};
  function applyLang(l, keepVideo) {
    UI = l; document.documentElement.lang = l === "zh" ? "zh-CN" : l;
    try { localStorage.setItem(A.slug + "-lang", l); } catch (e) {}
    document.querySelectorAll("[data-i18n]").forEach(function (el) { var v = T(el.getAttribute("data-i18n")); if (v !== undefined) el.textContent = v; });
    document.querySelectorAll("[data-i18n-ph]").forEach(function (el) { var v = T(el.getAttribute("data-i18n-ph")); if (v !== undefined) el.placeholder = v; });
    playBtn.textContent = playing ? T("pause") : T("play"); voiceBtn.textContent = voiceOn ? T("voiceOn") : T("voiceOff");
    document.querySelectorAll("#langs button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.l === l)); });
    renderChips(); renderForm();
    var cs = document.querySelector(".ctabox.static"); if (cs && A.cta) cs.innerHTML = '<b>' + esc(L(A.cta.title)) + '</b><span>' + esc(L(A.cta.line)) + '</span><i>' + esc(L(A.cta.button) || "→") + '</i>';
    if (CUR && !keepVideo) playCurrent();
  }
  LANGS.forEach(function (l) { var b = document.createElement("button"); b.type = "button"; b.dataset.l = l; b.textContent = (GEN[l] || GEN.en).name; b.onclick = function () { applyLang(l); }; $("langs").appendChild(b); });

  // ---------- owner key: ?owner=<token> once, then every request skips the limits ----------
  var OWNER = "";
  (function () {
    var u = new URL(location.href), o = u.searchParams.get("owner");
    try { if (o) localStorage.setItem(A.slug + "-owner", o); OWNER = localStorage.getItem(A.slug + "-owner") || localStorage.getItem("bka-owner") || ""; } catch (e) { OWNER = o || ""; }
    if (o) { u.searchParams.delete("owner"); history.replaceState(null, "", u.pathname + u.search); }
  })();
  function api(body) {
    var h = { "Content-Type": "application/json" }; if (OWNER) h["X-Owner-Token"] = OWNER;
    return fetch(A.api, { method: "POST", headers: h, body: JSON.stringify(body) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { return { ok: r.ok, status: r.status, d: d }; }); });
  }

  // ---------- run ----------
  var statusEl = $("status");
  function setStatus(m, err) { statusEl.textContent = m || ""; statusEl.className = "status" + (err ? " err" : ""); }
  function show(plan, link) {
    S = build(plan); t = 0; sceneIdx = -1; playing = true; idleSpin = false;
    playBtn.disabled = restartBtn.disabled = false; playBtn.textContent = T("pause");
    $("dl").disabled = false; $("share").disabled = false;
    shareLink = link || ""; details(plan);
    if (link && history.replaceState) history.replaceState(null, "", link.replace(location.origin, ""));
  }
  function linkFor() { var base = location.origin + location.pathname + "?"; if (LOCAL && !CUR.id) return base + "f=" + encodeURIComponent(packForm(CUR.form)) + (CUR.q ? "&q=" + encodeURIComponent(CUR.q) : "") + "&lang=" + UI; return CUR.id ? base + "example=" + CUR.id + "&lang=" + UI : base + "q=" + encodeURIComponent(CUR.q) + "&lang=" + UI; }
  function translateAndShow(source, store) {
    if (store[UI]) { show(store[UI], linkFor()); return; }
    var want = UI; S = null; idleMsg = T("translating"); idleSpin = true; $("plan").style.display = "none";
    api({ translate: source, lang: want }).then(function (res) {
      if (want !== UI) return;
      if (!res.ok || !res.d.plan) { show(source, linkFor()); setStatus(T("errFail"), true); return; }
      store[want] = res.d.plan; show(res.d.plan, linkFor()); setStatus("");
    }).catch(function () { show(source, linkFor()); });
  }
  function playCurrent() {
    if (!CUR) return;
    if (LOCAL) { var ex0 = CUR.id && EX[CUR.id], lp = LOCAL.answer(ex0 ? { form: ex0.form || {}, q: ex0.q[UI] || ex0.q.en || "" } : { form: CUR.form, q: CUR.q }, UI); if (lp && !lp.error) show(lp, linkFor()); return; }
    if (CUR.id) { var plans = EX[CUR.id].plans; if (plans[UI]) { show(plans[UI], linkFor()); return; } translateAndShow(plans.en || plans[Object.keys(plans)[0]], plans); return; }
    if (CUR.source.lang && CUR.source.lang.slice(0, 2) === UI) { show(CUR.source, linkFor()); return; }
    translateAndShow(CUR.source, TR);
  }
  var EX = {};
  function renderChips() {
    var chips = $("chips");
    Array.prototype.slice.call(chips.querySelectorAll(".chip")).forEach(function (c) { c.remove(); });
    Object.keys(EX).forEach(function (id) {
      var ex = EX[id], b = document.createElement("button"); b.type = "button"; b.className = "chip";
      b.textContent = ex.label[UI] || ex.label.en; b.title = ex.q[UI] || ex.q.en || "";
      b.onclick = function () { setForm(ex.form ? JSON.parse(JSON.stringify(ex.form)) : {}); $("q").value = ex.q[UI] || ex.q.en || ""; setStatus(""); CUR = { id: id }; playCurrent(); document.querySelector(".stage").scrollIntoView({ behavior: "smooth", block: "start" }); };
      chips.appendChild(b);
    });
  }
  // Local mode (A.local = URL of an advisor rules file that sets window.ADVISOR_LOCAL = {answer(input, lang), examples}):
  // the answer is computed in the browser from the form and keywords, so there is no API call, cost or daily limit.
  var LOCAL = null;
  var exReady = A.local ? new Promise(function (res) {
      var sc = document.createElement("script"); sc.src = A.local; sc.onload = sc.onerror = function () { res(); }; document.head.appendChild(sc); offs.push(function () { sc.remove(); });
    }).then(function () { LOCAL = window.ADVISOR_LOCAL || null; if (LOCAL) { (LOCAL.examples || []).forEach(function (ex) { EX[ex.id] = { label: ex.label, q: ex.q, form: ex.form || {} }; }); renderChips(); } })
    : fetch(location.pathname.replace(/\/$/, "") + "/examples.json").then(function (r) { return r.json(); }).then(function (d) { EX = d || {}; renderChips(); }).catch(function () {});
  applyLang(UI, true);

  var busy = false;
  function ask(q) {
    q = q.trim();
    if (q.length < 3 || busy) return;
    var ex = Object.keys(EX).find(function (id) { return Object.keys(EX[id].q).some(function (l) { return EX[id].q[l].toLowerCase() === q.toLowerCase(); }); });
    if (ex) { CUR = { id: ex }; playCurrent(); return; }
    busy = true; $("go").disabled = true;
    if (window.innerWidth < 720) document.querySelector(".stage").scrollIntoView({ behavior: "smooth", block: "start" });
    S = null; idleMsg = T("designing"); idleSpin = true; setStatus(""); $("plan").style.display = "none";
    api({ question: q })
      .then(function (res) {
        if (!res.ok || !res.d.plan) throw new Error(res.status === 429 ? (/resting/.test(res.d.error || "") ? T("errBusy") : T("errLimit")) : res.status === 503 ? (/offline/.test(res.d.error || "") ? T("errOffline") : T("errBusy")) : res.status === 422 ? (res.d.code === "offtopic" ? T("errTopic") : T("errNoPlan")) : res.status === 400 ? T("errShort") : T("errFail"));
        var plan = res.d.plan, pl = (plan.lang || "en").slice(0, 2);
        CUR = { q: q, source: plan }; TR = {}; TR[pl] = plan;
        if (LANGS.indexOf(pl) >= 0 && pl !== UI) applyLang(pl, true);
        playCurrent();
        if (typeof res.d.remaining === "number" && res.d.remaining < 900) setStatus(T("left").replace("{n}", res.d.remaining));
      })
      .catch(function (e) { idleSpin = false; idleMsg = e && e.message && !/fetch|network/i.test(e.message) ? e.message : T("errFail"); setStatus(idleMsg, true); })
      .then(function () { busy = false; $("go").disabled = false; });
  }
  function runLocal() {
    readForm(); var form = JSON.parse(JSON.stringify(formVals)), q = $("q").value.trim();
    var lp = LOCAL.answer({ form: form, q: q }, UI);
    if (!lp || lp.error) { setStatus(T(lp && lp.error === "topic" ? "errTopic" : "errShort"), true); return; }
    setStatus(""); CUR = { form: form, q: q }; show(lp, linkFor());
    if (window.innerWidth < 720) document.querySelector(".stage").scrollIntoView({ behavior: "smooth", block: "start" });
  }
  $("f").onsubmit = function (e) { e.preventDefault(); if (LOCAL) { runLocal(); return; } var q = compose(); if (q.length < 3) { setStatus(T("errShort"), true); return; } ask(q); };
  $("q").addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("f").onsubmit(e); } });
  var params = new URLSearchParams(location.search);
  exReady.then(function () {
    var id = params.get("example"), q = params.get("q");
    if (LOCAL && !(id && EX[id]) && (params.get("f") || q)) { setForm(unpackForm(params.get("f"))); $("q").value = q || ""; runLocal(); return; }
    if (id && EX[id]) { if (EX[id].form) setForm(JSON.parse(JSON.stringify(EX[id].form))); $("q").value = EX[id].q[UI] || EX[id].q.en || ""; CUR = { id: id }; playCurrent(); }
    else if (q) { $("q").value = q; ask(q); }
  });

  // ---------- full screen (phones rotate the video to landscape) ----------
  var screenEl = $("screen"), fsBtn = $("fsbtn"), tapHint = $("tapfs");
  function layoutFS() {
    if (!screenEl.classList.contains("fs")) return;
    var vw = window.innerWidth, vh = window.innerHeight, portrait = vh > vw;
    var longSide = portrait ? vh : vw, shortSide = portrait ? vw : vh, w = Math.min(longSide, shortSide * 16 / 9);
    screenEl.style.setProperty("--cw", w + "px"); screenEl.style.setProperty("--ch", (w * 9 / 16) + "px"); screenEl.style.setProperty("--rot", portrait ? "90deg" : "0deg"); screenEl.classList.toggle("rot", portrait);
  }
  function enterFS() {
    if (screenEl.classList.contains("fs")) return;
    screenEl.classList.add("fs"); document.body.classList.add("fs-open"); fsBtn.textContent = "✕"; fsBtn.setAttribute("aria-label", "Exit full screen"); layoutFS();
    var req = screenEl.requestFullscreen || screenEl.webkitRequestFullscreen;
    if (req) { try { var pr = req.call(screenEl); if (pr && pr.then) pr.then(function () { if (screen.orientation && screen.orientation.lock) screen.orientation.lock("landscape").catch(function () {}); }).catch(function () {}); } catch (e) {} }
    if (S && t >= S.total) { t = 0; sceneIdx = -1; playing = true; playBtn.textContent = T("pause"); }
  }
  function leaveFS(fromEvent) {
    if (!screenEl.classList.contains("fs")) return;
    screenEl.classList.remove("fs"); document.body.classList.remove("fs-open"); fsBtn.textContent = "⛶"; fsBtn.setAttribute("aria-label", "Full screen");
    if (!fromEvent && (document.fullscreenElement || document.webkitFullscreenElement)) { try { var ex = (document.exitFullscreen || document.webkitExitFullscreen).call(document); if (ex && ex.catch) ex.catch(function () {}); } catch (e) {} }
    try { screen.orientation && screen.orientation.unlock && screen.orientation.unlock(); } catch (e) {}
  }
  fsBtn.onclick = function (e) { e.stopPropagation(); screenEl.classList.contains("fs") ? leaveFS() : enterFS(); };
  cv.addEventListener("click", function () { if (S && window.matchMedia("(pointer: coarse)").matches && !screenEl.classList.contains("fs")) enterFS(); });
  on(document, "fullscreenchange", function () { if (!document.fullscreenElement) leaveFS(true); layoutFS(); });
  on(document, "webkitfullscreenchange", function () { if (!document.webkitFullscreenElement) leaveFS(true); layoutFS(); });
  on(document, "keydown", function (e) { if (e.key === "Escape") leaveFS(); });
  on(window, "resize", layoutFS); on(window, "orientationchange", function () { setTimeout(layoutFS, 250); });
  timers.push(setInterval(function () { tapHint.textContent = T("tap"); tapHint.style.opacity = S && t < 3 ? "1" : "0"; }, 500));

  function destroy() { alive = false; timers.forEach(clearInterval); offs.forEach(function (f) { f(); }); if (recorder) try { recorder.stop(); } catch (e) {} if ("speechSynthesis" in window) speechSynthesis.cancel(); leaveFS(); }
  window.__adv = { destroy: destroy, seek: function (s) { t = s; playing = false; render(Math.min(t, S.total - 0.001)); }, show: show, state: function () { return S && { total: S.total, lang: S.lang, starts: S.scenes.map(function (x) { return x.kind + "@" + x.start.toFixed(1); }).join(" ") }; } };
})();
