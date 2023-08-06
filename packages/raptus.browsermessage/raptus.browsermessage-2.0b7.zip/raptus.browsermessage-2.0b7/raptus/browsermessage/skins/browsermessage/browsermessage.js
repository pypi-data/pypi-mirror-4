jQuery(document).ready(function($) {
  $("#browsermessage #ignore").click(function() {
    $.get('browsermessage_ignore', {}, function() {
      $('#browsermessage').remove();
      $('#browsermessage-overlay').remove();
    });
    return false;
  });
});