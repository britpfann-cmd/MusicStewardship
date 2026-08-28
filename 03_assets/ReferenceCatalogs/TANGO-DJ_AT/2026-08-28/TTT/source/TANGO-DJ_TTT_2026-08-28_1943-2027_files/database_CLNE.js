//
// v2.7 (18.07.2026): reCAPTCHA-Relikt onSubmit(token) entfernt (Cleanup, T37).
// Token-Handling laeuft ausschliesslich ueber js/turnstile-gate.js.
//

function setOnlineStatus(seed, key) {
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
  console.log("calling ->", url);
  $.getJSON(url);
  //
}

function clearForm() {
  var oForm = document.getElementById('search');
  var elements = oForm.elements;
  oForm.reset();
  for(i=0; i<elements.length; i++) {
    clearElement(elements[i]);
  }
}

function clearSearchForm() {
  var oForm = document.getElementById('search');
  var elements = oForm.elements;
  for(i=0; i<elements.length; i++) {
    switch (elements[i].id) {
      case 'recommended':
      case 'mediumCD':
      case 'mediumLP':
      case 'mediumSP':
      case 'mediumDG':
      case 'mediumAny':
      case 'mediumOther':
      case 'sortingTitle':
      case 'sortingAlbum':
      case 'sortingArtist':
      case 'sortingDate':
      case 'searchModeFlexible':
      case 'searchModeRegular':
      case 'searchModeStrict':
      case 'everywhere':
        // nothing so far
      break;
      //
      default:
        clearElement(elements[i]);
      break;
    }
  }
}

function clearFullSearchForm() {
  var oForm = document.getElementById('search');
  var elements = oForm.elements;

  for(i=0; i<elements.length; i++) {
    switch (elements[i].id) {
      case 'everywhere':
        clearElement(elements[i]);
      break;
      //
      default:
      // nothing so far
      break;
    }
  }
}

function clearElement(element) {

  field_type = element.type.toLowerCase();

  switch(field_type) {

    case "text":
    case "password":
    case "textarea":
    case "hidden":

    element.value = "";
    break;

    case "radio":
    case "checkbox":
    if (element.checked) {
      element.checked = false;
    }
    break;

    case "select-one":
    case "select-multi":
    element.selectedIndex = 0;
    break;

    default:

    break;
  }
}

function setSelectionRange(input, selectionStart, selectionEnd) {
  if (input.setSelectionRange) {
    input.focus();
    input.setSelectionRange(selectionStart, selectionEnd);
  } else if (input.createTextRange) {
    var range = input.createTextRange();
    range.collapse(true);
    range.moveEnd('character', selectionEnd);
    range.moveStart('character', selectionStart);
    range.select();
  }
}

function setCaretToPos(input, pos) {
  setSelectionRange(input, pos, pos);
}

function setCaretPosition(input, pos) {
  input.setSelectionRange(pos, pos);
  input.focus();
}

function initInput() {
  console.log('initInput() (disabled) ->', $("#message")[0]);
  if (false) {
    $("#message").click(function() {
      setCaretPosition($("#message")[0], 10); // /!\ 10 depends on textarea content...
    });
  }
}

// =====================================================================
// v3.1.0: Lyrics Popup (Magnific Popup inline type)
// =====================================================================
$(document).on('click', '.lyrics-popup-link', function(e) {
  e.preventDefault();
  var target = $(this).attr('href');
  $.magnificPopup.open({
    items: {
      src: target,
      type: 'inline'
    },
    closeBtnInside: true,
    mainClass: 'mfp-fade'
  });
});