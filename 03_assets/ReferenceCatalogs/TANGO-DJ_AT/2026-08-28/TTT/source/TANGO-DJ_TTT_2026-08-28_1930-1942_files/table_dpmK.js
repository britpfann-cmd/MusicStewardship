
// v2.7 (18.07.2026): reCAPTCHA-Relikt onSubmit(token) entfernt (Cleanup, T37).
// Zielte auf 'form1', das nicht existiert — toter Code.

function initTable() {
  //
  initFavorite();
  //
  initSorting();

  var sels = $('select');
  for (var i = 0; i < sels.length; i++) {
    sel = sels[i];
    if (sel.title.length) {
      for (var j = 0; j < sel.options.length; j++) {
        if (sel.options[j].value == sel.title) {
          sel.options[j].selected = true;
          break;
        }
      }
    }
  }
  //
  $(".tablesorter th").addClass("sort_header");
  // $(".tablesorter").tablesorter({
  //   widgets: ["zebra"]
  // });
  $(".tablesorter tr").mouseover(function() {
    $(this).addClass("over");
  });
  $(".tablesorter tr").mouseout(function() {
    $(this).removeClass("over");
  });
  //
  console.log('initTable');
  //
  // v3.3.0: Ribbon-Toggle-State wiederherstellen
  ribInitToggles();
}
//
// Show/Hide columns and fields
//
function setStyleHide(name) {
  $('#' + name).text('.style' + name + '{display: none}');
  // console.log('Hiding # ' + name);
}
//
function setStyleShow(name) {
  $('#' + name).text('.style' + name + '{}');
  // console.log('Showing # ' + name);
}

function toggleRecommended() {
  // var value = document.getElementById('recommended').value
  var value = window.config.recommended;
  if (value) {
    value = false;
    $('#hideRecommended').text('.hideRecommended {}');
  } else {
    value = true;
    $('#hideRecommended').text('.hideRecommended {display: none}');
  }
  window.config.recommended = value;
  console.log('toggleRecommended -> ', value, ' = ', $('#hideRecommended').text());
}

function toggleInstrumental() {
  var value = window.config.instrumentalFilter;
  if (value) {
    value = false;
    $('#hideNonInstrumental').text('.hideNonInstrumental {}');
  } else {
    value = true;
    $('#hideNonInstrumental').text('.hideNonInstrumental {display: none}');
  }
  window.config.instrumentalFilter = value;
  console.log('toggleInstrumental -> ', value, ' = ', $('#hideNonInstrumental').text());
}

function hideColumn(name) {
  key  = 0;
  seed = 0;
  $("#resetButtonStyle").text('.resetButton {opacity: 1.0}');
  setStyleHide(name);
  url = "php/column-js.php?f=hide&g=" + name + "&h=" + key + "&i=" + seed;
  $.getJSON(url);
  // console.log(url);
}

function showAllColumn() {
  key  = 0;
  seed = 0;
  $("#resetButtonStyle").text('.resetButton {opacity: 0.5}');
  for(var key in window.config.columnNameList) {
    name = window.config.columnNameList[key];
    setStyleShow(name);
  }
  setStyleShow('AuthorComposer');
  url = "php/column-js.php?f=show&g=all&h=" + key + "&i=" + seed;
  $.getJSON(url);
  // console.log(url);
}
//
function initSorting() {
  //
  // $.extend( $.tablesorter.characterEquivalents, {
  //   "A"  : "Á",
  //   "ae" : "\u00e6", // expanding characters æ Æ
  //   "AE" : "\u00c6",
  //   "oe" : "\u00f6\u0153", // œ Œ
  //   "OE" : "\u00d6\u0152",
  //   "d"  : "\u00f0",  // Eth (ð Ð)
  //   "D"  : "\u00d0",
  //   "o"  : "\u00f3\u00f2\u00f4\u00f5", // remove ö because it's in the oe now
  //   "O"  : "\u00d3\u00d2\u00d4\u00d5"  // remove Ö because it's in the OE now
  // });

  tableSorterParam = { };
  // tableSorterParam['headers']  = window.config.headers;
  tableSorterParam['sortList'         ] = window.config.sortList;
  tableSorterParam['debug'            ] = window.config.debug;
  tableSorterParam['textExtraction'   ] = function(node) {
    return $(node).attr('data-sort-value') || $(node).text();
  }
  //tableSorterParam['sortLocaleCompare'] = true;
  //tableSorterParam['debug'            ] = false;
  //
  $("#searchresult").tablesorter(tableSorterParam);
  console.log('tableSorterParam =', tableSorterParam);
}
//
function initFavorite() {
  $("div.favorite").each(function(index) {
    $(this).click(function() {
      toggleFavorite(index + 1, this);
    });
  });
};

function toggleFavorite(index, thing) {
  key = 0;
  seed = 0;
  id = $(thing).attr("data");
  var idx = window.config.favoriteList.indexOf(id);
  if (idx == -1) {
    $(thing).addClass("f_on");
    window.config.favoriteList.push(id);
    url = "php/favorite-js.php?f=set&g=" + id + "&h=" + key + "&i=" + seed;
    $.getJSON(url);
    console.log('click on adding ', id, window.config.favoriteList);
  } else {
    $(thing).removeClass("f_on");
    window.config.favoriteList.splice(idx, 1)
    url = "php/favorite-js.php?f=unset&g=" + id + "&h=" + key + "&i=" + seed;
    $.getJSON(url);
    console.log('click on delete ', id, window.config.favoriteList);
  }
}
//
function OBSsetOnlineStatus(seed, key) {
  state = document.getElementById("online").checked;
  node = document.getElementById("status");
  if (state) {
    value = 1;
    node.style.color = "green";
    node.textContent = "online";
  } else {
    value = 0;
    node.style.color = "red";
    node.textContent = "maintenance (results may be incomplete)";
  }
  url = "php/config-js.php?g=" + value + "&h=" + key + "&i=" + seed;
  $.getJSON(url);
  //
}

// =====================================================================
// v3.3.0: Ribbon Toggle-Wrapper
// =====================================================================

function ribToggleRecommended() {
  // Bestehende CSS-Klassen-Logik aufrufen
  toggleRecommended();
  // Active-Klasse am Ribbon-Button synchronisieren
  var btn = document.getElementById('ribRecommended');
  if (btn) {
    if (window.config.recommended) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  }
  // Hidden Input synchronisieren (für Formular-State)
  var hidden = document.getElementById('recommended');
  if (hidden && hidden.type === 'hidden') {
    hidden.value = window.config.recommended ? '1' : '0';
  }
}

function ribToggleInstrumental() {
  // Bestehende CSS-Klassen-Logik aufrufen
  toggleInstrumental();
  // Active-Klasse am Ribbon-Button synchronisieren
  var btn = document.getElementById('ribInstrumental');
  if (btn) {
    if (window.config.instrumentalFilter) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  }
  // Hidden Input synchronisieren (für Formular-State)
  var hidden = document.getElementById('instrumental');
  if (hidden && hidden.type === 'hidden') {
    hidden.value = window.config.instrumentalFilter ? '1' : '0';
  }
}

// Ribbon-State beim Laden wiederherstellen
function ribInitToggles() {
  if (window.config.recommended) {
    var btn = document.getElementById('ribRecommended');
    if (btn) btn.classList.add('active');
  }
  if (window.config.instrumentalFilter) {
    var btn = document.getElementById('ribInstrumental');
    if (btn) btn.classList.add('active');
  }
}
