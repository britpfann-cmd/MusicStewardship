// ============================================================================
// turnstile-gate.js — Cloudflare Turnstile, Phase 1 MONITORING  |  T37
// v2.4.0 (07.08.2026) — Patch: Token-Parameter nach dem Seitenaufbau aus der
//   Adresszeile entfernen (tsGateCleanUrl(), via history.replaceState).
//   ANLASS: Such-URLs sind zum Weitergeben an Kunden gedacht, enthielten aber
//   das Turnstile-Token (~600 Zeichen, durch einen zweiten Fehler sogar
//   doppelt). Das Token ist ein EINMAL-Token: der Empfaenger eines solchen
//   Links laeuft anonym in 'invalid' -> block_invalid -> Sperrmeldung, waehrend
//   derselbe Link OHNE Token ueber den no_token-Retry-Pfad sauber funktioniert.
//   Derselbe Fehler traf jeden Reload (F5) einer Trefferseite: dasselbe Token
//   ein zweites Mal -> 'duplicate'/'invalid' -> Sperrmeldung "please reload the
//   page", also genau die Aktion, die den Fehler ausloest (belegt in
//   tango_turnstile_stats, 05./06.08.2026: member duplicate 5+1, invalid 4+2).
//   Am Token-TRANSPORT aendert sich nichts — Monitoring und Enforcement sehen
//   die Parameter unveraendert, geputzt wird erst danach im Browser.
// v2.3.0 (03.08.2026) — Admin 2.9 Patch: reset()+execute() ersetzt durch
//   remove()+render()+execute() in tsGateGetToken() (Fix fuer dokumentierten
//   Cloudflare-Bug: Widget bleibt nach reset() unsichtbar, wenn beim ersten
//   execute() keine Interaktion noetig war -- auch wenn eine spaetere Anfrage
//   eine sichtbare Challenge braeuchte). tsGateInit() nutzt jetzt denselben
//   Render-Pfad (tsGateRenderWidget()). Timeout bleibt 5000 ms (bewusst nicht
//   erhoeht). Siehe Turnstile-Diagnose-Session 02.08.2026 (Riccardo Biemmi).
// v2.2.1 (18.07.2026) — Admin 2.7 Patch: Wartekringel in die ECHTE Summary-Line
//   (#summary-line) statt in eine Extra-Zeile darueber (die die Summary-Line nach
//   unten schob). Sperrmeldung weiter zentriert einzeilig.
// v2.2.0 (18.07.2026) — Admin 2.7 Patch: Kringel/Meldung zentriert (Statuszeile).
// v2.1.0 (18.07.2026) — Admin 2.7 Patch: News-/DB-Such-Links ohne index.htm werden
//   jetzt auch getokent (+Origin-Rewrite gegen www-Redirect); Loop-Guard via window.name.
// v2.0.0 (18.07.2026) — Admin 2.7 (Enforcement: Re-Execute + Button-Spinner)
// v1.0.0 (16.07.2026) — Admin 2.6
// ============================================================================
// Haengt an jede Suche ein Turnstile-Token an:
//   1. Suchformular #search (GET-Submit): Token als Hidden-Field
//      "cf-turnstile-response" vor dem Submit.
//   2. Ergebnis-/News-/Ribbon-Links auf index.htm?... : Klick abfangen,
//      Token holen, als &cf_ts=... an die URL haengen, dann navigieren.
//
// PHASE-1-GRUNDSATZ: darf NIE eine Suche verhindern. Jeder Fehlerpfad
// (API nicht geladen, Blocker, Timeout, execute-Fehler) laesst die Aktion
// nach kurzer Frist OHNE Token durchlaufen — der Server zaehlt das dann
// als "no_token"/"fail_open", blockt aber nicht.
//
// Voraussetzungen (head.htm):
//   <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=tsGateInit&render=explicit" async defer></script>
//   <script src="js/turnstile-gate.js"></script>
// Widget-Container (search-form.php, von PHP mit Sitekey gerendert):
//   <div id="ts-widget" data-sitekey="..."></div>
//
// Kein jQuery-Zwang: pures DOM-API (jQuery 1.9 ist zwar da, aber diese
// Datei soll auch bei jQuery-Problemen funktionieren).
// Namensraum tsGate* — die reCAPTCHA-Relikte onSubmit(token) in
// database.js/table.js bleiben unberuehrt (form1 existiert ohnehin nicht).
// ============================================================================

var tsGate = {
  el:        null,   // Widget-Container (#ts-widget) -- fuer Re-Render gebraucht
  sitekey:   null,
  widgetId:  null,
  ready:     false,
  timeoutMs: 5000,   // Fail-Safe: so lange warten wir maximal auf ein Token
                     // 22.07.2026: 2500 -> 5000. Grund: execution:'execute' holt
                     // das Token ERST im Klickmoment (Live-Roundtrip zu
                     // challenges.cloudflare.com).
                     // 02./03.08.2026 -- Diagnose ergab: der Haupt-Ausloeser fuer
                     // ausgeschoepfte 5 s war NICHT Netz-Latenz, sondern ein
                     // dokumentierter Cloudflare-Bug (reset() vor jedem execute()
                     // laesst eine noetig gewordene Challenge unsichtbar haengen,
                     // siehe tsGateGetToken()-Kommentar). Fix dort behoben den
                     // eigentlichen Fall -- Timeout bewusst NICHT erhoeht (Bernhard,
                     // 03.08.2026: "kein User wartet so lange, wenn er nicht vorab
                     // eine lange Wartezeit erwartet"). Bleibt bei 5000 ms.
  execBusy:  false
};

// ---------------------------------------------------------------------------
// Widget (neu) rendern. Ausgelagert, weil sowohl der initiale Aufbau
// (tsGateInit) als auch jede Token-Anforderung (tsGateGetToken, s.u.) einen
// frischen Render brauchen.
// ---------------------------------------------------------------------------
function tsGateRenderWidget() {
  if (!tsGate.el || typeof turnstile === 'undefined') return null;
  try {
    return turnstile.render(tsGate.el, {
      sitekey:   tsGate.sitekey,
      execution: 'execute',          // Token nur on-demand holen
      callback:  function (token) { tsGateDeliver(token); },
      'error-callback':   function () { tsGateDeliver(''); },
      'expired-callback': function () { /* naechstes execute holt neu */ },
      appearance: 'interaction-only' // unsichtbar, solange keine Interaktion noetig
    });
  } catch (e) {
    return null;
  }
}

// Callback der Turnstile-API (?onload=tsGateInit).
function tsGateInit() {
  var el = document.getElementById('ts-widget');
  if (!el || typeof turnstile === 'undefined') return;
  var sitekey = el.getAttribute('data-sitekey') || '';
  if (!sitekey) return;
  tsGate.el      = el;
  tsGate.sitekey = sitekey;
  tsGate.widgetId = tsGateRenderWidget();
  tsGate.ready    = (tsGate.widgetId !== null);
}

// ---------------------------------------------------------------------------
// Token-Beschaffung mit Fail-Safe-Timer. done(token) wird GENAU EINMAL
// gerufen — mit Token oder mit '' (Timeout/Fehler/API fehlt).
// ---------------------------------------------------------------------------
tsGate._pending = null;

function tsGateDeliver(token) {
  if (tsGate._pending) {
    var cb = tsGate._pending.cb;
    clearTimeout(tsGate._pending.timer);
    tsGate._pending = null;
    tsGate.execBusy = false;
    cb(token || '');
  }
}

function tsGateGetToken(done) {
  if (!tsGate.ready || tsGate.widgetId === null || tsGate.execBusy) {
    done('');   // API fehlt (Blocker) oder parallele Anforderung -> ohne Token
    return;
  }
  tsGate.execBusy = true;
  tsGate._pending = {
    cb:    done,
    timer: setTimeout(function () { tsGateDeliver(''); }, tsGate.timeoutMs)
  };
  try {
    // v2.9-Patch (02./03.08.2026): reset()+execute() ersetzt durch
    // remove()+render()+execute(). Bekannter Cloudflare-Bug (Community-Thread
    // "Widget not displayed in interaction-only mode after turnstile.reset()"):
    // wenn beim ERSTEN execute() eines Widgets keine Interaktion noetig war,
    // bleibt das Widget nach einem reset() unsichtbar -- AUCH WENN eine
    // spaetere Anfrage (z.B. hoeheres Risiko durch VPN/Datacenter-Exit-IP)
    // eigentlich eine sichtbare Challenge braeuchte. execute() haengt dann
    // ohne jede UI bis zum Fail-Safe-Timeout -- exakt das beobachtete
    // "haengt bei ~50% der Suchen"-Symptom (Riccardo Biemmi/wp_user_id 700,
    // Diagnose-Session 02.08.2026). Ein frischer render() (statt reset())
    // erzeugt eine neue Widget-Instanz ohne diese "already-passed"-Historie
    // und zeigt eine noetige Challenge zuverlaessig an, statt sie zu
    // verstecken. Kosten: minimal zusaetzlicher DOM-Overhead pro Suche
    // (remove+render statt reset) -- vernachlaessigbar gegen das Ziel, echte
    // Token-Zustellung zu ermoeglichen. Single-Use-Semantik bleibt erhalten:
    // jede Suche bekommt ein frisches Widget, exakt wie vorher mit reset().
    if (tsGate.widgetId !== null) {
      turnstile.remove(tsGate.widgetId);
    }
    tsGate.widgetId = tsGateRenderWidget();
    if (tsGate.widgetId === null) {
      tsGateDeliver('');
      return;
    }
    turnstile.execute(tsGate.widgetId);
  } catch (e) {
    tsGateDeliver('');
  }
}

// ---------------------------------------------------------------------------
// 1) Formular-Intercept: erstes Submit anhalten, Token holen, weiterreichen.
// ---------------------------------------------------------------------------
document.addEventListener('submit', function (ev) {
  var form = ev.target;
  if (!form || form.id !== 'search') return;
  if (form.getAttribute('data-ts-done') === '1') {
    form.removeAttribute('data-ts-done');   // Token haengt schon dran
    return;
  }
  if (!tsGate.ready) return;                // kein Widget -> normal submitten
  ev.preventDefault();
  // Button-Spinner erst nach 150 ms zeigen — bei warmem Widget kommt das Token
  // schneller und es gibt keinen Flackerer. Nur der Button wird gesperrt,
  // das Formular bleibt bedienbar.
  var _spinTimer = setTimeout(function () { tsGateStatusSpinner(true); }, 150);
  tsGateGetToken(function (token) {
    clearTimeout(_spinTimer);
    if (token) {
      var f = document.getElementById('ts-token-field');
      if (!f) {
        f = document.createElement('input');
        f.type = 'hidden';
        f.name = 'cf-turnstile-response';
        f.id   = 'ts-token-field';
        form.appendChild(f);
      }
      f.value = token;
    }
    form.setAttribute('data-ts-done', '1');
    // submit() feuert das submit-Event NICHT erneut in allen Browsern —
    // das data-Attribut sichert die Browser ab, die es doch tun.
    form.submit();
  });
}, true);

// ---------------------------------------------------------------------------
// 2) Link-Interceptor: Treffer-Spalten, News, Favorite, Feedback —
//    alles, was per GET auf index.htm eine Suche ausloest.
//    Nur linke Maustaste ohne Modifier (Cmd/Ctrl/Shift-Klick = neuer Tab,
//    den lassen wir unangetastet durchlaufen -> zaehlt als no_token).
// ---------------------------------------------------------------------------
document.addEventListener('click', function (ev) {
  if (ev.defaultPrevented) return;
  if (ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
  var a = ev.target;
  while (a && a.nodeName !== 'A') a = a.parentNode;
  if (!a || !a.href) return;
  if (a.classList && a.classList.contains('lyrics-popup-link')) return;
  if (a.target && a.target !== '' && a.target !== '_self') return;   // neuer Tab -> unangetastet
  // v2.7-Fix: Such-Link erkennen ueber den PFAD, nicht ueber "index.htm?".
  // News-"Updates"-Links haben die Form  https://tango-dj.at/database/?...  (OHNE
  // index.htm, teils OHNE www) und wurden vorher nicht getokent -> landeten als
  // no_token -> Enforcement-Sperre + Retry-Schleife. Jetzt matchen beide Formen:
  //   .../database/index.htm?...   UND   .../database/?...
  var path = a.pathname || '';
  if (path.charAt(0) !== '/') path = '/' + path;        // alte Browser liefern ohne fuehrenden /
  var isSearch = /\/database\/(index\.htm)?$/.test(path) && a.search && a.search.length > 1;
  if (!isSearch) return;
  if (a.search.indexOf('cf_ts=') !== -1) return;        // schon getokent
  if (!tsGate.ready) return;                            // kein Widget -> normal navigieren
  //
  ev.preventDefault();
  var _spinTimerL = setTimeout(function () { tsGateStatusSpinner(true); }, 150);
  // Ziel auf die AKTUELLE Origin umschreiben: News-Links zeigen teils auf
  // tango-dj.at (ohne www). Ohne Rewrite wuerde der www-301-Redirect Query +
  // Token schlucken -> no_token-Schleife. Gleiche Origin = kein Redirect.
  var base;
  if (a.hostname && a.hostname !== window.location.hostname && /(^|\.)tango-dj\.at$/i.test(a.hostname)) {
    base = window.location.protocol + '//' + window.location.host + path + a.search + (a.hash || '');
  } else {
    base = a.href;
  }
  tsGateGetToken(function (token) {
    clearTimeout(_spinTimerL);
    var url = base;
    if (token) {
      url += (url.indexOf('?') === -1 ? '?' : '&') + 'cf_ts=' + encodeURIComponent(token);
    }
    window.location.href = url;
  });
}, true);


// ===========================================================================
// v2.7 Patch: Wartekringel ZENTRIERT in die Statuszeile (#ts-status-line,
// Summary-Line-Position). Verschiebt weder Such-Button noch Formular — anders
// als die alte Variante, die den Kringel neben den Button setzte.
// ===========================================================================
function tsGateStatusSpinner(on) {
  // Kringel in die ECHTE Summary-Line (#summary-line, von summary-line.php immer
  // gerendert) schreiben — NICHT in eine separate Zeile darueber. Sonst entsteht
  // zwischen Formular und Summary-Line eine zusaetzliche Zeile, die diese nach
  // unten schiebt. Fallback #ts-status-line nur, falls #summary-line fehlt
  // (z.B. auf der Block-/Retry-Seite, wo die Summary-Line uebersprungen wird —
  // dort wird aber ohnehin kein Kringel gezeigt).
  var line = document.getElementById('summary-line') || document.getElementById('ts-status-line');
  if (!line) return;
  if (on) {
    // display:block + text-align:center -> mittig, unabhaengig vom Alignment
    // der Summary-Line.
    line.innerHTML = '<span class="ts-status-msg" style="display:block;text-align:center;"><span class="ts-spin" role="status" aria-label="Searching"></span></span>';
  } else {
    line.innerHTML = '';
  }
}

// Spinner-Style einmalig injizieren (Keyframe braucht ein <style>).
(function tsGateInjectStyle() {
  if (document.getElementById('ts-gate-style')) return;
  var st = document.createElement('style');
  st.id = 'ts-gate-style';
  st.textContent =
      '.ts-status-line:empty{display:none;}'
    + '.ts-status-line{text-align:center;padding:10px 0;line-height:1.4;}'
    + '.ts-status-msg{display:inline-block;font-size:14px;color:#333;}'
    + '.ts-status-block{color:var(--dark-red,#5f0000);font-weight:600;}'
    + '.ts-spin{display:inline-block;width:14px;height:14px;'
    + 'vertical-align:middle;border:2px solid rgba(95,0,0,.25);'
    + 'border-top-color:var(--dark-red,#5f0000);border-radius:50%;'
    + 'animation:tsspin .7s linear infinite;}'
    + '@keyframes tsspin{to{transform:rotate(360deg);}}';
  (document.head || document.documentElement).appendChild(st);
})();

// ===========================================================================
// v2.7: Re-Execute bei tokenlosem Einstieg (geteilte/getippte Such-URL,
// Bookmark). Der Server (search.php, mode=on + no_token_mode=fail_closed) hat
// die Suche zurueckgehalten und index.htm setzt window.tsGateRetry=true. Wir
// warten bis das Widget warm ist, holen ein Token und wiederholen die Suche
// GENAU EINMAL (ts_retry-Marker in der URL schuetzt vor Endlosschleife).
// ===========================================================================
function tsGateShowBlocked() {
  var line = document.getElementById('ts-status-line');
  if (line) {
    line.innerHTML = '<span class="ts-status-msg ts-status-block">Search could not be verified \u2013 please reload the page.</span>';
  }
}
// ---------------------------------------------------------------------------
// v2.4.0: Token-Parameter aus der Adresszeile entfernen.
//
// Entfernt werden 'cf-turnstile-response' (Formular-Submit), 'cf_ts'
// (Link-Interceptor) und 'ts_retry' (Retry-Marker). Alles andere bleibt
// unangetastet, ebenso der Row-Hash-Anchor (#...) aus v3.3.2.
//
// ts_retry MUSS mit raus: bliebe der Marker im weitergegebenen Link, wuerde er
// beim Empfaenger den Nachhol-Versuch unterdruecken (search.php prueft
// !isset($_GET['ts_retry'])) und ihn direkt in die Sperrmeldung schicken.
//
// Aufgerufen wird das NUR, wenn gerade kein Retry laeuft (siehe
// tsGateReExecute) — waehrend des Retrys braucht der Ablauf seine Marker noch.
// Im Sperr-Fall wird ebenfalls geputzt: ein anschliessendes F5 laedt dann die
// saubere URL, landet auf no_token und kommt ueber den Retry-Pfad durch,
// statt mit demselben verbrauchten Token erneut aufzulaufen.
// ---------------------------------------------------------------------------
function tsGateCleanUrl() {
  if (!window.history || !window.history.replaceState) return;   // alte Browser
  var loc = window.location;
  if (!loc.search || loc.search.length < 2) return;
  var parts   = loc.search.substring(1).split('&');
  var keep    = [];
  var removed = false;
  for (var i = 0; i < parts.length; i++) {
    if (parts[i] === '') continue;
    var eq   = parts[i].indexOf('=');
    var name = (eq === -1) ? parts[i] : parts[i].substring(0, eq);
    if (name === 'cf-turnstile-response' || name === 'cf_ts' || name === 'ts_retry') {
      removed = true;
      continue;
    }
    keep.push(parts[i]);
  }
  if (!removed) return;
  var url = loc.pathname + (keep.length ? '?' + keep.join('&') : '') + (loc.hash || '');
  try {
    window.history.replaceState(null, '', url);
  } catch (e) {
    // Fail-safe: bleibt die URL wie sie ist, aendert sich nur nichts.
  }
}

function tsGateReExecute() {
  if (!window.tsGateRetry) {
    // Normale (nicht-Verifying) Seite erreicht -> Loop-Guard zuruecksetzen,
    // damit ein spaeterer echter Kalt-Einstieg wieder retrien darf.
    if (window.name === 'ts_gate_retried') { window.name = ''; }
    tsGateCleanUrl();   // v2.4.0: Adresszeile kopierfaehig hinterlassen
    return;
  }
  window.tsGateRetry = false;   // nur einmal pro Seitenaufbau
  // Origin-uebergreifender Loop-Schutz: window.name ueberlebt Navigation im
  // selben Tab auch ueber www/no-www hinweg (anders als der ts_retry-Query-
  // Marker, den ein 301-Redirect schlucken kann). Waren wir schon einmal hier,
  // NICHT nochmal navigieren -> Sperrmeldung statt endlos "Verifying".
  if (window.name === 'ts_gate_retried') {
    window.name = '';
    tsGateShowBlocked();
    return;
  }
  window.name = 'ts_gate_retried';
  var waited = 0;
  var iv = setInterval(function () {
    if (tsGate.ready) {
      clearInterval(iv);
      tsGateGetToken(function (token) {
        var url = window.location.href;
        if (url.indexOf('ts_retry=') === -1) {
          url += (url.indexOf('?') === -1 ? '?' : '&') + 'ts_retry=1';
        }
        if (token) { url += '&cf_ts=' + encodeURIComponent(token); }
        window.location.replace(url);
      });
    } else if (waited >= 4000) {
      // Widget kam nicht hoch (Blocker/CF weg). Ein Versuch mit Marker; der
      // Server zeigt dann (fail_closed) die Sperrmeldung, statt endlos zu warten.
      clearInterval(iv);
      var url2 = window.location.href;
      if (url2.indexOf('ts_retry=') === -1) {
        url2 += (url2.indexOf('?') === -1 ? '?' : '&') + 'ts_retry=1';
      }
      window.location.replace(url2);
    }
    waited += 100;
  }, 100);
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', tsGateReExecute);
} else {
  tsGateReExecute();
}
