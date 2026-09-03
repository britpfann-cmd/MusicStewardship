// v3.3.3.2 - News Click Tracker
// ==============================
// Fix: Linktext wird jetzt aus data-link-text Attribut gelesen statt aus textContent.
// Verhindert dass Browser-Übersetzungs-Plugins (Google Translate etc.) den
// geloggten Linktext verfälschen — der Original-Text aus news.json wird korrekt erfasst.
//
// Aufgespielte Sections:
//   - 'permanent'  → dauerhafte Links oben im News-Widget
//   - 'updates'    → aktuelle News-Eintraege
//   - 'history'    → Eintraege im History-Tab bzw auf database-news-history.htm
//   - 'manual'     → Manual-Icon im Ribbon
//
// Container muss ein data-news-section-Attribut tragen:
//   <div data-news-section="updates"> ... <a href="..." data-link-text="Original Text"> ... </a> ... </div>
//
// Fuer das Manual-Icon: Element mit id="manual-icon-track" oder Klasse .manual-track
//

(function () {
  'use strict';

  var ENDPOINT = '/database/php/news-click-log.php';

  function sendClick(url, text, section) {
    try {
      if (!url) return;
      var data = new URLSearchParams();
      data.append('url', url);
      data.append('text', (text || '').substring(0, 200));
      data.append('section', section || 'updates');

      if (navigator.sendBeacon) {
        navigator.sendBeacon(ENDPOINT, data);
      } else {
        // Fallback: synchroner kleiner XHR (Safari alt / IE)
        var xhr = new XMLHttpRequest();
        xhr.open('POST', ENDPOINT, true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.send(data.toString());
      }
    } catch (e) {
      // silent
    }
  }

  function attachNewsHandlers() {
    // Alle Container mit data-news-section finden
    var containers = document.querySelectorAll('[data-news-section]');
    for (var i = 0; i < containers.length; i++) {
      var section = containers[i].getAttribute('data-news-section');
      var links = containers[i].querySelectorAll('a[href]');
      for (var j = 0; j < links.length; j++) {
        attachLink(links[j], section);
      }
    }

    // Manual-Icon getrennt (keine News-Container)
    var manualIcons = document.querySelectorAll('.manual-track, #manual-icon-track');
    for (var k = 0; k < manualIcons.length; k++) {
      attachLink(manualIcons[k], 'manual');
    }
  }

  function attachLink(el, section) {
    if (el._newsTracked) return;
    el._newsTracked = true;
    el.addEventListener('click', function () {
      var href = el.getAttribute('href') || '';
      // data-link-text hat Vorrang vor textContent — schützt vor Browser-Übersetzungs-Plugins
      var text = (el.getAttribute('data-link-text') || el.getAttribute('title') || el.textContent || '').trim();
      sendClick(href, text, section);
    }, true);  // Capture-Phase: wird vor Navigation ausgeloest
  }

  // Zweifach: einmal beim Laden, einmal bei DOM-Aenderungen (News werden nachgeladen)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachNewsHandlers);
  } else {
    attachNewsHandlers();
  }

  // Falls News per AJAX nachgeladen werden: MutationObserver
  if (window.MutationObserver) {
    var observer = new MutationObserver(function () {
      attachNewsHandlers();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }
})();
