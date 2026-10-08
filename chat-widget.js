/* TapeBackup assistant: floating "Ask about LTO" chat. Talks to /api/chat. */
(function () {
  if (window.__tbChat) return;
  window.__tbChat = true;
  var lang = (document.documentElement.lang || "en").slice(0, 2);
  var T = {
    en: ["Ask about LTO", "Ask the TapeBackup assistant", "Short answers on LTO tape, backup software and our videos. 3 questions per day.", "e.g. How much does an LTO-9 tape cost?", "Ask", "Thinking…", "questions left today"],
    de: ["Frag zu LTO", "TapeBackup-Assistent", "Kurze Antworten zu LTO-Band, Backup-Software und unseren Videos. 3 Fragen pro Tag.", "z. B. Was kostet ein LTO-9-Band?", "Fragen", "Denke nach…", "Fragen heute übrig"],
    fr: ["Une question LTO ?", "Assistant TapeBackup", "Réponses courtes sur la bande LTO, les logiciels de sauvegarde et nos vidéos. 3 questions par jour.", "ex. Combien coûte une cartouche LTO-9 ?", "Demander", "Réflexion…", "questions restantes aujourd'hui"],
    it: ["Chiedi su LTO", "Assistente TapeBackup", "Risposte brevi su nastro LTO, software di backup e i nostri video. 3 domande al giorno.", "es. Quanto costa un nastro LTO-9?", "Chiedi", "Sto pensando…", "domande rimaste oggi"],
    es: ["Pregunta sobre LTO", "Asistente de TapeBackup", "Respuestas breves sobre cinta LTO, software de copia de seguridad y nuestros vídeos. 3 preguntas al día.", "p. ej. ¿Cuánto cuesta una cinta LTO-9?", "Preguntar", "Pensando…", "preguntas restantes hoy"],
    nl: ["Vraag over LTO", "TapeBackup-assistent", "Korte antwoorden over LTO-tape, back-upsoftware en onze video's. 3 vragen per dag.", "bijv. Wat kost een LTO-9-tape?", "Vraag", "Even denken…", "vragen over vandaag"],
    pl: ["Zapytaj o LTO", "Asystent TapeBackup", "Krótkie odpowiedzi o taśmach LTO, oprogramowaniu do backupu i naszych filmach. 3 pytania dziennie.", "np. Ile kosztuje taśma LTO-9?", "Zapytaj", "Myślę…", "pytań zostało na dziś"]
  }[lang] || null;
  T = T || ["Ask about LTO", "Ask the TapeBackup assistant", "Short answers on LTO tape, backup software and our videos. 3 questions per day.", "e.g. How much does an LTO-9 tape cost?", "Ask", "Thinking…", "questions left today"];

  var css = ".tbc-btn{position:fixed;right:20px;bottom:20px;z-index:9998;display:flex;align-items:center;gap:8px;padding:12px 18px;border:0;border-radius:999px;background:#5b27d6;color:#fff;font:600 15px/1 'Hanken Grotesk',system-ui,sans-serif;box-shadow:0 8px 24px rgba(91,39,214,.35);cursor:pointer}" +
    ".tbc-btn:hover{background:#4a1fb4}.tbc-btn svg{width:18px;height:18px}" +
    ".tbc-panel{position:fixed;right:20px;bottom:80px;z-index:9999;width:min(380px,calc(100vw - 32px));max-height:min(560px,calc(100vh - 120px));display:none;flex-direction:column;background:#fff;color:#161320;border:1px solid #e4e1ec;border-radius:18px;box-shadow:0 18px 50px rgba(22,19,32,.18);font:15px/1.5 'Hanken Grotesk',system-ui,sans-serif;overflow:hidden}" +
    ".tbc-panel.open{display:flex}.tbc-head{padding:16px 18px 12px;background:#f7f6fa;border-bottom:1px solid #e4e1ec;position:relative}" +
    ".tbc-head b{display:block;font:700 16px/1.3 'Space Grotesk',system-ui,sans-serif}.tbc-head small{display:block;color:#6e6a7c;margin-top:4px;font-size:13px}" +
    ".tbc-x{position:absolute;right:12px;top:12px;border:0;background:none;font-size:20px;line-height:1;color:#6e6a7c;cursor:pointer}" +
    ".tbc-log{flex:1;overflow-y:auto;padding:14px 18px;display:flex;flex-direction:column;gap:10px}" +
    ".tbc-q{align-self:flex-end;max-width:85%;background:#5b27d6;color:#fff;padding:8px 12px;border-radius:14px 14px 4px 14px}" +
    ".tbc-a{align-self:flex-start;max-width:92%;background:#f7f6fa;padding:10px 12px;border-radius:14px 14px 14px 4px;white-space:pre-line}" +
    ".tbc-a a{color:#5b27d6;word-break:break-all}.tbc-a.err{background:#fdf0ee;color:#8a2a20}" +
    ".tbc-form{display:flex;gap:8px;padding:12px;border-top:1px solid #e4e1ec}" +
    ".tbc-form input{flex:1;min-width:0;padding:10px 12px;border:1px solid #d6d2e2;border-radius:10px;font:inherit}" +
    ".tbc-form input:focus{outline:2px solid #5b27d6;outline-offset:-1px}" +
    ".tbc-form button{padding:10px 14px;border:0;border-radius:10px;background:#5b27d6;color:#fff;font:600 14px/1 inherit;cursor:pointer}" +
    ".tbc-form button:disabled{opacity:.5;cursor:default}.tbc-left{padding:0 18px 10px;color:#6e6a7c;font-size:12px}" +
    "@media (max-width:520px){.tbc-btn{right:12px;bottom:12px}.tbc-panel{right:12px;bottom:68px}}";
  var st = document.createElement("style");
  st.textContent = css;
  document.head.appendChild(st);

  var btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tbc-btn";
  btn.setAttribute("aria-expanded", "false");
  btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg><span></span>';
  btn.querySelector("span").textContent = T[0];

  var panel = document.createElement("div");
  panel.className = "tbc-panel";
  panel.setAttribute("role", "dialog");
  panel.setAttribute("aria-label", T[1]);
  panel.innerHTML = '<div class="tbc-head"><b></b><small></small><button type="button" class="tbc-x" aria-label="Close">×</button></div>' +
    '<div class="tbc-log" aria-live="polite"></div><div class="tbc-left"></div>' +
    '<form class="tbc-form"><input type="text" maxlength="400" required><button type="submit"></button></form>';
  panel.querySelector("b").textContent = T[1];
  panel.querySelector("small").textContent = T[2];
  var input = panel.querySelector("input"), send = panel.querySelector(".tbc-form button"), log = panel.querySelector(".tbc-log"), left = panel.querySelector(".tbc-left");
  input.placeholder = T[3];
  input.setAttribute("aria-label", T[1]);
  send.textContent = T[4];

  function toggle(open) {
    panel.classList.toggle("open", open);
    btn.setAttribute("aria-expanded", String(open));
    if (open) input.focus();
  }
  btn.addEventListener("click", function () { toggle(!panel.classList.contains("open")); });
  panel.querySelector(".tbc-x").addEventListener("click", function () { toggle(false); btn.focus(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && panel.classList.contains("open")) { toggle(false); btn.focus(); } });

  function bubble(cls, text) {
    var d = document.createElement("div");
    d.className = cls;
    // Safe linkify: text nodes plus <a> elements only for http(s) URLs.
    String(text).split(/(https?:\/\/[^\s<>"']+)/g).forEach(function (part, i) {
      if (i % 2) {
        var a = document.createElement("a");
        a.href = part; a.textContent = part.replace(/^https?:\/\//, ""); a.rel = "noopener"; a.target = "_blank";
        d.appendChild(a);
      } else d.appendChild(document.createTextNode(part));
    });
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    return d;
  }

  panel.querySelector("form").addEventListener("submit", function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (!q) return;
    bubble("tbc-q", q);
    input.value = "";
    send.disabled = true;
    var wait = bubble("tbc-a", T[5]);
    fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: q, lang: lang }) })
      .then(function (r) { return r.json().catch(function () { return { error: "Error " + r.status }; }); })
      .then(function (d) {
        wait.remove();
        var text = d.answer || d.error || "";
        var links = (d.links || []).filter(function (l) { return text.indexOf(l) < 0; });
        if (links.length) text += "\n" + links.join("\n");
        bubble(d.answer ? "tbc-a" : "tbc-a err", text);
        if (typeof d.remaining === "number") left.textContent = d.remaining + " " + T[6];
        if (d.remaining === 0) { input.disabled = true; send.disabled = true; return; }
        send.disabled = false;
        input.focus();
      })
      .catch(function () { wait.remove(); bubble("tbc-a err", "Network error."); send.disabled = false; });
  });

  document.body.appendChild(panel);
  document.body.appendChild(btn);
})();
