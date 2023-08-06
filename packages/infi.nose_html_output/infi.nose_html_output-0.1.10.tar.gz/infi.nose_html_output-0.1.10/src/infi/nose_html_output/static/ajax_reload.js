
function do_refresh(html_data) {
    $(document.body).html(html_data);
}

function do_ajax_reload() {
    $.ajax({url: "http://localhost:16193/", crossDomain: true, dataType: "jsonp"});
}

$(document).ready(function() {
    do_ajax_reload();
});