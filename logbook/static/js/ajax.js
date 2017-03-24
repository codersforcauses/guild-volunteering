$(document).ready(function() {
    
});
    
function doAjax(checkboxid, bookid, action){
    
    var rowId = '#row-'+checkboxid;
    var badge = '#badge-'+bookid;
    $(badge).text($(badge).text()-1);
    $(rowId).remove();
    
    $.ajax({
        type: "post",
        url: "./updatehrs/",
        data: { selectedAction: action, model_selected:checkboxid, book_id:bookid, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()},
        success: function(data) {

        }
    });
}


form = document.getElementById('modelForm');
var actions = document.getElementById('actions');

function doOne(checkboxid, action) {
    document.getElementById(checkboxid).checked = true;
    actions.value = action;
}

function submitAll(tableid) {
    table = document.getElementById(tableid);
    checkboxes = table.querySelectorAll('[name=model_selected]');
    for (var i=0; i<checkboxes.length; i++) {
        checkboxes[i].checked = true;
    }
    actions.value = 'approve';

}


function getCookie(name) {
    var cookieValue = null;
    var i = 0;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (i; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
}); 
