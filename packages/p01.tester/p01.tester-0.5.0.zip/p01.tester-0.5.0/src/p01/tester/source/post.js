jQuery(document).ready(function ($) {
    // load asap
    $.ajax({
        url: "http://localhost:9090/post-first.html",
        type: 'POST',
        dataType: 'json',
        processData: false,
        async: false,
        success: function(data, textStatus) {
          $('#result').html(data.result);
          $('#status').html(textStatus);
        },
        error: function(jqXHR, textStatus, errorThrown) {
          $('#result').html("FIRST ERROR");
          $('#status').html(textStatus);
        }
    });
});

