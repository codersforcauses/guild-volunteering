$(document).ready(function() {
    
});

//Used for ajax requests on editing logbooks
function loadBook(book_id) {
    
    //$('#edit_form').attr("action", './edit_book/'+book_id+'/');
    
    $.ajax({
       type:"get",
       url:"./load_book/",
       contentType:'application/json',
       data: {book_id:book_id},
       success: function(output) {
           $('#edit_form_name').val(output.name);
           //See Django form to see where the id for this comes from
           $('#edit_form_category').val($('#edit_form_category option:contains("'+output.category+'")').index());
       }
    });
    
    $('#edit_form').append('<input type="hidden" id="book_id" name="book_id" value="'+ book_id +'"/>');
    
    return false;
}

function loadEntry(entry_id, action) {
    $.ajax({
       type:"get",
       url:"../load_entry/",
       contentType:'application/json',
       data: { entry:entry_id },
       success: function(output) {
            if (action === 'edit'){
                $('#edit_form_name').val(output.name);
                //See Django form to see where the id for this comes from
                $('#edit_form_supervisor').val(output.supervisor);
                $('#edit_form_start').val(output.start);
                $('#edit_form_end').val(output.end);
            } else if (action === 'add') {
                $('#add_name').val('('+output.name+')');
                $('#add_supervisor').val(output.supervisor);
            }
       }
    });
    
    $('#edit_form').append('<input type="hidden" id="entry_id" name="entry_id" value="'+ entry_id +'"/>');
    
    return false;
}

function doAjax(checkboxid, bookid, action){
    
    var rowId = '#row-'+checkboxid;
    var badge = '#badge-'+bookid;
    $(badge).text($(badge).text()-1);
    $(rowId).remove();
    console.log($(badge).text());
    if ($(badge).text() === '0') {
        console.log('Yes');
        $('#'+bookid).remove();
        $('#entry-'+bookid).remove();
        $('#entry-'+bookid).hide();
    }
        
    $.ajax({
        type: "post",
        url: "./update_approvals/",
        data: { selectedAction: action, model_selected:checkboxid, book_id:bookid, csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()},
        success: function(data) {

        }
    });
    return false;
}

var form = document.getElementById('modelForm');
var actions = document.getElementById('actions');
    
function doAction(action) {
    actions.value = action;
    form.submit();
}

//Random thing, idk where it belongs :(
$("[title]").tooltip();

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
    form.submit();

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
