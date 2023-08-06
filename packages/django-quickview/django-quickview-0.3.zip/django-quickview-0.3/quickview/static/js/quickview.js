<!-- handy functions -->
function dump_array(data, printer_func){
    $.each(data, function(index, value){
        if (printer_func != undefined)
            printer_func(value);
        else
            console.log(value);
    });
}

function populate_table(table, fields, rows)
{
    var header = $(table).append($('<tr></tr>'));
    for (var fieldIndex = 0; fieldIndex < fields.length; fieldIndex++)
    {
        $(table).$("tbody").append($('<th>' + fields[fieldIndex]+ '</th>'));
    }

    for (var rowIndex = 0; rowIndex < rows.length; rowIndex++)
    {
        var r = $(table).$("tbody").append($('<tr></tr>'));
        for (var fieldIndex = 0; fieldIndex < fields.length; fieldIndex++)
            r.append($('<td>' + rows[rowIndex][fields[fieldIndex]]+ '</td>'));
    }

}

function get_form_values(form)
{
    return $(form).serialize();
}

function iterator(data, item_handler){
    $.each(data.object_list, function(i, item) {
        item_handler(item);
    })
}

function dummy_handler(data)
{
    console.log(data);
}

function ajax_call(csrf_token, url, params, success_handler, failure_handler)
{
    if (success_handler == undefined)
        success_handler = dummy_handler;

    if (failure_handler == undefined)
        failure_handler = dummy_handler;

    params['csrfmiddlewaretoken'] = csrf_token;
    $.ajax({
        url: url,
        type: "post",
        data: params,
        success: function(data){
            success_handler(data);
        },
        error:function(data){
            failure_handler(data);
        }
    });
}
