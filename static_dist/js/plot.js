 $('.show-plot').click(function (e) {
    $('form#plot-form').toggle();
});

$('body').on('submit', 'form#plot-form',function (e) {

    e.preventDefault();
    if(! (plot_un && plot_key)){
        $('#set_un').modal('toggle');
        return false
    }
    var x_asis = $(this).find('select[name="xasis"]').val();
    var y_asis = $(this).find('select[name="yasis"]').val();

    if (x_asis === null){
        $(this).find('select[name="xasis"]').closest('div').addClass('has-error');
        return false
    }
    if (y_asis === null){
        $(this).find('select[name="yasis"]').closest('div').addClass('has-error');
        return false
    }
    $(this).find('select[name="xasis"]').closest('div').removeClass('has-error');
    $(this).find('select[name="yasis"]').closest('div').removeClass('has-error');

    var plot_type = $(this).find('select[name="plot_type"]').val();

    var plot_data = {};
    plot_data['un'] = plot_un;
    plot_data['key'] = plot_key;
    plot_data['origin'] = 'plot';
    plot_data['platform'] = 'javascript';

    var table = $("#dataTable");
    var handsontable = table.data('handsontable');

    var plot_args = table_to_plot_data(handsontable.getData());
    var args = [plot_args[x_asis], plot_args[y_asis]];
    plot_data['args'] = JSON.stringify(args);

    plot_data['kwargs'] = JSON.stringify({"filename": "plot for {{ object }}",
                           "fileopt": "overwrite",
                                "style": {
                                    "type": plot_type
                                },
                            "layout": {
                                "title": "plot for {{ object }}"
                            },
                            "world_readable": true
                            });
    $.post('https://plot.ly/clientresp', plot_data, function( data ) {
        var plot_url =JSON.parse(data).url;
        $('.plot-link').html('<p><a target="_blank" href="' + plot_url + '">View the plot on plot.ly</a></p>')
    });
});

function reset_plot() {
  $('form#plot-form').hide();
  $('.plot-link').html('')
  $('select[name="xasis"] option:first-child').attr("selected", "selected");
  $('select[name="yasis"] option:first-child').attr("selected", "selected");

}

function table_to_plot_data(table_data) {
    // Remove table headers
    table_data = table_data.slice(1);

    // Remove empty row from end
    for(var i = table_data.length-1; i > 1; i -= 1){
        var flag_empty = true;
        for(var j = 0, max2 = table_data[i].length; j < max2; j += 1){
            if(table_data[i][j] ){
                flag_empty = false
                break
            }
        }
        if (flag_empty) {
            table_data.splice(-1, 1)
        } else {
        break
        }
    }
    // Initialize plot_data object
    var plot_data = []
    for (var i = 0, max = table_data[0].length; i < max; i += 1) {
        plot_data.push([])
    }

    // Fill plot_data object
    for (var i = 0, max = table_data.length; i < max; i += 1) {
        for (var j = 0, max2 = table_data[i].length; j < max2; j += 1) {
            plot_data[j].push(table_data[i][j])
        }
    }
    return plot_data
}

 $(function() {
     var table = $("#dataTableEditable");
     if (table.length){
         var options = $(table).handsontable('getDataAtRow', 0);
         $('#plot-form .asis').find('option').not( ":disabled" ).remove().end();
         if(options){
             for (var i = 0, max = options.length; i < max; i += 1) {
                 $('#plot-form .asis').append('<option value="'+ i +'">' + options[i] + '</option>')
             }
         }

     }

 });
