$(document).ready(function() {
  //
  // play audio files
  //
  var playing = 0;
  var played  = 0;
  // BUG: need to plug globals in window object: ugly, ugly, ugly!
  window.fadeIn  = 100;
  window.fadeOut = 100;

  function resetAllButton() {
    $("div.play-button").each(function(index) {
      $(this).removeClass("pause");
    });
  }
  //
  function togglePlay(index, fadeIn, fadeOut, $button) {
    // console.log('togglePlay', index, $button);
    finalize = function() {
      if (playing == index) {
        playing = 0;
        resetAllButton();
        $button.toggleClass("play");
      } else {
        playing = index;
        playAudio(index, fadeIn);
        resetAllButton();
        $button.toggleClass("pause");
      }
    }
    if (playing != 0) {
      stopAudio(playing, fadeOut, finalize);
    } else {
      finalize();
    }
  }
  //
  function playAudio(index, fadeIn) {
    // console.log('playAudio', index);
    var audio = $('#player');
    var player = document.getElementById("player");
    data = $("#button-" + index).attr("data");
    path = '/database-data/' + data + '.mp3';
    // console.log('path', path);
    //
    // v3.3.3: Play-Analytics (sendBeacon = non-blocking, silent-fail)
    //
    try {
      if (navigator.sendBeacon) {
        var _parts = data.split('/');
        if (_parts.length === 2) {
          navigator.sendBeacon('php/play-log.php?id=' + encodeURIComponent(_parts[1]));
        }
      }
    } catch (e) { /* silent */ }
    //
    if (index != played) {
      player.src = path;
    }
    player.play();
    audio.animate({
      volume: 1.0
    }, fadeIn);
  }
  //
  function stopAudio(index, fadeOut, finalize) {
    // console.log('stopAudio', index, finalize);
    var audio = $('#player');
    var player = document.getElementById("player");
    audio.animate({
      volume: 0.0
    }, fadeOut, function() {
      player.pause();
      finalize();
    });
    played = playing;
  }
  //
  function initPlayButtons() {
    $("div.play-button").each(function(index) {
      // console.log('initPlayButtons #', index);
      $(this).click(function() {
        var fadeIn  = window.fadeIn;
        var fadeOut = window.fadeOut;
        togglePlay(index + 1, fadeIn, fadeOut, $(this));
      });
    });
  }
  //
  console.log('initPlayButtons');
  initPlayButtons();
  //
  // FIXME: kludge to reload on back/forward buttons
  //
  // var $input = $('#refresh');
  // if ($input.val() == 'yes') {
  //   location.reload(true);
  //   // alert('Reloaded...');
  // } else {
  //   $input.val('yes');
  // }
  //
});
