function strip_tags(input, allowed) {
    // +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    allowed = (((allowed || "") + "").toLowerCase().match(/<[a-z][a-z0-9]*>/g) || []).join(''); // making sure the allowed arg is a string containing only tags in lowercase (<a><b><c>)
    var tags = /<\/?([a-z][a-z0-9]*)\b[^>]*>/gi,
        commentsAndPhpTags = /<!--[\s\S]*?-->|<\?(?:php)?[\s\S]*?\?>/gi;
    return input.replace(commentsAndPhpTags, '').replace(tags, function ($0, $1) {
        return allowed.indexOf('<' + $1.toLowerCase() + '>') > -1 ? $0 : '';
    });
}

function ColorLuminance(hex, lum) {

    // validate hex string
    hex = String(hex).replace(/[^0-9a-f]/gi, '');
    if (hex.length < 6) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    lum = lum || 0;

    // convert to decimal and change luminosity
    var rgb = "#", c, i;
    for (i = 0; i < 3; i++) {
        c = parseInt(hex.substr(i * 2, 2), 16);
        c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
        rgb += ("00" + c).substr(c.length);
    }
    return rgb;
}

function treeValueToJson(value, column, col) {
    try {
        value = JSON.parse(value);
    } catch (e) {
        var column_value = column[col].selectOptions || '',
            values = value.split(',');
        value = [];
        for (var j = 0, jmax = column_value.length; j < jmax; j++) {
            for (var v = 0; v < values.length; v++) {
                if (column_value[j].text == values[v]) {
                    value.push({"text": column_value[j].text, "color": column_value[j].li_attr.background_color});
                }
            }
        }
    }
    return value;
}


$(function () {
    if ($("#dataTable").length) {
        addHandsonTable("#dataTable");
    }
});

function getTableData(url) {
    var get_data = null;
    jQuery.ajaxSetup({async: false});
    $.get(url, function (data) {
        get_data = data;
    })

    jQuery.ajaxSetup({async: true});
    f = []
    if (get_data.constructor === Array){
        for (var i in get_data) {
            var array = $.map(get_data[i], function (value, index) {
                return [value];
            });
            f[i] = array
        }
    } else {
        f[0] = get_data['headers']
        Array.prototype.push.apply(f, get_data['table_data'])
    }
    return f;
}

function addHandsonTable(selector) {
    var table = $(selector),
        title = table.data('title'),
        headers = table.data('headers'),
        toUpperCase = function (match) {
            return match.toUpperCase();
        },
        column = table.data('column'),

        data = getTableData(table.data('content-url')),
        colWidths = [],
        getHeight = function (){
            var sidebar_height = $('.main-sidebar').height();
            return sidebar_height - 150
        },
        renderTags = function (instance, td, row, col, prop, value, cellProperties) {
            var escaped, style = '',
                values;
            if (value && !(value instanceof Array)) {
                value = treeValueToJson(value, column, col);
            }
            if (value) {
                values = [].map.call(value, function (val) {
                    escaped = Handsontable.helper.stringify(val.text);
                    escaped = strip_tags(escaped, '<em><b><strong><a><big>');
                    style = '' +
                        'box-shadow: 0 0 2px ' + ColorLuminance(val.color, -0.5) + ' inset, 0 1px 0 rgba(0, 0, 0, 0.05);' +
                        'background-color:' + val.color + '; border: 1px solid ' + val.color;
                    return '<span class="tags" style="' + style + '">' + escaped + '</span>';
                }).join('');
            } else {
                values = Handsontable.helper.stringify(value);
            }
            td.innerHTML = values;
            return td;
        },
        handsontable;

    for (var i = 0, max = column.length; i < max; i += 1) {
//        if (column[i].validator_string){
//            column[i].validator = new RegExp(column[i].validator_string)
//        }
        if (column[i].display == 'none') {
            colWidths.push(0.01);
        } else {
            colWidths.push(200);
        }
        if (column[i].renderer == 'renderTags') {
            column[i].renderer = renderTags;
        }
    }

    table.handsontable({
        data: data,
        columns: column,
        fillHandle: true,
        minRows: 1,
        autoWrapCol: false,
        manualColumnResize: true,
        manualRowResize: true,
        minSpareRows: 1,
        colWidths: colWidths,
        height: getHeight,
        colHeaders: function (col) {
            if (headers[col]) {
                if (typeof column !== 'undefined' && typeof column[col] !== 'undefined' && column[col].hasOwnProperty('append_url')) {
                    return headers[col].replace(/(?:^|\s)./g, toUpperCase) + ' <a href="#" class="btn btn-default append" data-toggle="modal" ' +
                        'data-target="#' + (column[col].modal_id || 'modal') + '" data-url="' + column[col].append_url + '" data-column="' + col + '">+</a>';
                } else {
                    return headers[col].replace(/(?:^|\s)./g, toUpperCase);
                }
            }
        },
        outsideClickDeselects: false,
        afterChange: function (changes, source) {
            $('.append').on('click', function (e) {
                $('div' + $(e.target).data('target') + ' form').attr('action', $(this).data('url')).attr('data-column', $(this).data('column'));
            });
            if (this.$table) {
                var tableContainer = this.$table.parents('div.handsontable'),
                    height = this.$table.height();
                if (tableContainer.css('min-height') != height) {
                    tableContainer.css('min-height', height).css('height', 'auto');
                    $('.wrap-handsontable').css('max-height', $(window).height() - $('.wrap-handsontable').offset().top - 30);
                }
            }

            var col, row, values, column_value, id, i, max, j, jmax, v, requiredCol;
            if (source == 'paste' || source == 'autofill') {
                for (i = 0, max = changes.length; i < max; i++) {
                    col = changes[i][1];
                    row = changes[i][0];
                    column_value = column[col].selectOptions || '';
                    id = [];
                    if (!column[col].readonly) {
                        if (column[col].editor == 'jstree') {
                            values = treeValueToJson(changes[i][3], column, col);
                            for (j = 0, jmax = column_value.length; j < jmax; j++) {
                                for (v = 0; v < values.length; v++) {
                                    if (column_value[j].text == values[v].text && column_value[j].li_attr.background_color == values[v].color) {
                                        id.push(column_value[j].id);
                                    }
                                }
                            }
                        } else {
                            values = changes[i][3].split(',');
                            for (j = 0, jmax = column_value.length; j < jmax; j++) {
                                for (v = 0; v < values.length; v++) {
                                    if (column_value[j][1] == values[v]) {
                                        id.push(column_value[j][0]);
                                    }
                                }
                            }
                        }
                        requiredCol = getRequiredCol(this, col, title);
                        if (requiredCol) {
                            this.setDataAtCell(row, requiredCol, id);
                        }
                    } else {
                        this.setDataAtCell(row, col, 'True');
                    }
                }
            } else if (source == 'edit') {
                for (i = 0, max = changes.length; i < max; i++) {
                    if (!changes[i][3].length) {
                        col = changes[i][1];
                        row = changes[i][0];
                        requiredCol = getRequiredCol(this, col, title);
                        if (requiredCol) {
                            this.setDataAtCell(row, requiredCol, '');
                        }
                    }
                }
            }
        },
        cells: function (row, col, prop) {
            var n_cols = table.handsontable('countCols');
            var i = 0;
            col = null;
            for (i; i < n_cols; i++) {
                if (table.handsontable('getColHeader', i).toLowerCase() === 'readonly') {
                    col = i;
                }
            }
            if (col != null) {
                var cellProperties = {};
                if (table.handsontable('getDataAtCell', row, col) === '' &&
                    (typeof column[col].default_value === 'undefined' || !(column[col].default_value))) {
                    cellProperties.readOnly = true;
                }
                return cellProperties;
            }
        },
        contextMenu: {
            items: {
                "row_above": {},
                "row_below": {},
                "hsep1": "---------",
                "remove_row": {
                    name: 'Remove selected rows',
                    callback: function (key, selection) {
                        var dataPost = [], dataRemove = [];
                        var ht = table.handsontable('getInstance');
                        var selected = ht.getSelected();
                        var start = Math.min(selected[0], selected[2]);
                        var end = Math.max(selected[0], selected[2]);
                        var pk;

                        for (var i = end, max = start; i >= max; i -= 1) {
                            pk = handsontable.getDataAtCell(i, 0);
                            if (typeof pk !== "undefined" && pk && pk.length) {
                                dataPost.push(pk);
                            } else {
                                this.alter("remove_row", i, 1);
                            }
                        }
                        if (dataPost.length) {
                            var that = this;
                            $.post(table.data('remove-url'), {'data': dataPost.join(',')})
                                .done(function (response) {
                                    var data = response.data,
                                        i, j, hasError = false,
                                        max = data.length,
                                        messages = [];
                                    for (i = 0; i < max; i += 1) {
                                        if (typeof data[i].errors != 'undefined' && messages.indexOf(data[i].errors.non_field_error) == -1) {
                                            messages.push(data[i].errors.non_field_error);
                                            hasError = true;
                                        } else {
                                            for (j = selection.start.row; j < (selection.end.row + 1); j += 1) {
                                                if (handsontable.getDataAtCell(j, 0) == data[i]) {
                                                    that.alter("remove_row", j, 1);
                                                }
                                            }
                                        }
                                    }
                                    showMessageChild(hasError, messages);
                                }).fail(function (xhr) {
                                    showMessageChild(true, [xhr.statusText]);
                                });
                        }
                        return (table.handsontable('getData').length === 1);
                    }
                }
            }
        }
    });

    handsontable = table.data('handsontable');

    $('#save').click(function () {

        var dataPost = [];
        var data = handsontable.getData();
        for (var i = 0, max = data.length; i < max; i += 1) {
            d = {}
            for (var key in data[i]) {
                if (data[i].hasOwnProperty(key) && data[i][key]) {
                    d[Object.keys(title).filter(function (item) {
                        return title[item] === headers[key]
                    })[0]] = data[i][key];
                }
            }
            for (var key in d) {
                if (key.indexOf(' ') >= 0) {
                    d[key.split(' ').join('_')] = d[key]
                    delete d[key]
                }

                if (key.substr(-3) == '_pk') {
                    delete d[key.slice(0, -3)]
                    d[key.slice(0, -3)] = d[key]
                    delete d[key]
                }
            }
            dataPost.push(d);
        }

        for (var key in dataPost) {
            if(key.substr(-3)== '_pk') {
                delete dataPost[key.slice(0, -3)]
                dataPost[key.slice(0, -3)] = dataPost[key]
                delete dataPost[key]
            }
        }

        dataPost.length = data.length;
        $.post(table.data('update-url'), JSON.stringify(dataPost)).done(function (res) {
            $('td').removeClass('error').removeAttr('title');
            var messages = [],
                hasError = false;
            for (var i = 0, max = res.length; i < max; i += 1) {
                var row = parseInt(res[i][0]),
                    result = res[i][1];
                if (result.success === true) {
                    handsontable.setDataAtCell(row, 0, result.pk);
                } else {
                    var tr = $('tr:nth-child(' + (row + 1) + ')'),
                        errors = result.errors;
                    hasError = true;
                    for (var name in errors) {
                        if (errors.hasOwnProperty(name)) {
                            tr.find('td:nth-child(' + (headers.indexOf(title[name]) + 1) + ')')
                                .attr('title', errors[name].join(',')).addClass('error');
                        }
                    }
                    if (typeof data[i].errors != 'undefined' && messages.indexOf(data[i].errors.non_field_error) == -1) {
                        messages.push(errors.non_field_error);
                    }
                }
            }
            showMessageChild(hasError, messages);

        }).fail(function (xhr) {
            showMessageChild(true, [xhr.statusText]);
        });
    });

    $('.append').on('click', function (e) {
        $('div' + $(e.target).data('target') + ' form').attr('action', $(this).data('url')).attr('data-column', $(this).data('column'));
    });

    submitForm($('.modal-form'), function (response, form) {
        var col = column[parseInt(form.data('column'))];
        col.selectOptions.push([response.pk, response.name]);
        col.validator = new RegExp((col.validator_string + '|' + response.name));
        $('.modal').modal('hide');
    });

    //overwrite getCopyable that tags copy right
    var copyableLookup = Handsontable.helper.cellMethodLookupFactory('copyable', false);

    /**
     * Returns single value from the data array (intended for clipboard copy to an external application)
     * @param {Number} row
     * @param {Number} prop
     * @return {String}
     */
    Handsontable.DataMap.prototype.getCopyable = function (row, prop) {
        if (copyableLookup.call(this.instance, row, this.propToCol(prop))) {
            var value = this.get(row, prop);
            if (column[prop].editor == 'jstree') {
                return [].map.call(value, function (val) {
                    return val.text;
                })
            }
            return value;
        }
        return '';
    };

    function getRequiredCol(table, col, title) {
        var n_cols = table.countCols(),
            name = (Object.keys(title).filter(function (item) {
                return title[item].toLowerCase() === table.getColHeader(col).split('<')[0].trim().toLowerCase()
            })[0] + '_pk').toLowerCase();
        for (var j = 1; j <= n_cols; j++) {
            if (typeof table.getColHeader(j) !== 'undefined' && name == table.getColHeader(j).toLowerCase()) {
                return j;
            }
        }
    }
}


function addHandsonTableEditable(selector, data) {

    var table = $(selector),
        title = 'table',
        toUpperCase = function (match) {
            return match.toUpperCase();
        },
        column = [
            {'editor': 'text', 'display': 'none'},
            {'editor': 'text', 'display': 'none'}],
        getHeight = function (){
            var sidebar_height = $('.main-sidebar').height();
            return sidebar_height - 150
        },
        colWidths = [],
        handsontable;

    for (var i = 0, max = column.length; i < max; i += 1) {
            colWidths.push(200);
    }

    if (!data) {
        data = getTableData(table.data('content-url'))
    }

    table.handsontable({
        data: data,

        autoWrapCol: false,
        minSpareRows: 1,
        contextMenu: true,
        colWidths: 200,
        outsideClickDeselects: false,
        height:getHeight(),
        afterChange: function (changes, source) {
            // update plot form
            var options = $(table).handsontable('getDataAtRow', 0);
            $('#plot-form .asis').find('option').not( ":disabled" ).remove().end();
            if(options) {
                for (var i = 0, max = options.length; i < max; i += 1) {
                    $('#plot-form .asis').append('<option value="'+ i +'">' + options[i] + '</option>')
                }
            }

        },
        cells: function (row, col, prop) {
            var cellProperties = {};
            if (row === 0) {
                cellProperties.renderer = firstRowRenderer; // uses function directly
            }
            return cellProperties;
        }
    });

    handsontable = table.data('handsontable');

    function getRequiredCol(table, col, title) {
        return false
    }

    function getColumnHeaders(table) {
        return $(table).handsontable('getDataAtRow', 0);
    }

    function firstRowRenderer(instance, td, row, col, prop, value, cellProperties) {
        Handsontable.renderers.TextRenderer.apply(this, arguments);
        td.style.color = '#222';
        td.style.backgroundColor = '#EEE';
        td.style.textAlign = 'center';
    }

};

showMessageChild = function (hasError, messages) {
    var error = gettext('Please fill in all required fields'),
        success = gettext('Your data has been saved.');
    if (messages.length == 0){messages.push(hasError ? error : success)}
    while (messages.length !== 0) {
        showMessage(hasError, messages.pop())

    }
};