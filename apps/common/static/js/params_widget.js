(function ($) {
    $.fn.dictEditor = function (json, options) {
        options = options || {};
        // Make sure functions or other non-JSON data types are stripped down.
        json = JSON.parse(JSON.stringify(json));
        console.log(json);

        json = sortOnKeys(json);
        console.log(json);

        var K = function () {
        };
        var onchange = options.change || K;

        return this.each(function () {
            DICTEditor($(this), json, onchange);
        });

    };

    function sortOnKeys(dict) {

        var sorted = [];
        for (var key in dict) {
            sorted[sorted.length] = key;
        }
        function SortByName(a, b) {
            var aName = a.toLowerCase();
            var bName = b.toLowerCase();
            return ((aName < bName) ? -1 : ((aName > bName) ? 1 : 0));
        }

        sorted.sort(SortByName);

        var tempDict = {};
        for (var i = 0; i < sorted.length; i++) {
            tempDict[sorted[i]] = dict[sorted[i]];
        }

        return tempDict;
    }

    function addButton(target, json, opt) {
        var el = $('<button class="append-item btn btn-default btn-flat btn-block">\n' +
            '  <i class="fa fa-plus"></i> ' + gettext('Add') + ' ' + gettext('property') + '\n</button>'
        );
        el.click(function (e) {
            e.preventDefault();
            construct(target, {"": ""}, opt);
        });
        target.append(el);
        return false;
    }

    function DICTEditor(target, json, onchange, keyElement, valueElement) {
        var opt = {
            propertyElement: keyElement,
            valueElement: valueElement,
            onchange: onchange
        };
        addButton(target, json, opt);
        construct(target, json, opt);

    }

    function jsonChange(e) {
        var path = {};
        e.data.target.find('div.item').each(function () {
            var input = $(this),
                key = input.find('#property').val(),
                value = input.find('#value').val();
            if (key || value) path[key] = value;
        });
        path = sortOnKeys(path);
        e.data.opt.onchange(path);
    }

    function construct(target, json, opt) {
        for (var key in json) {
            if (!json.hasOwnProperty(key)) continue;

            var item = $('<div>', {'class': 'item'}),
                div_row = $('<div>', {'class': 'row'}),
                div_property = $('<div>', {'class': 'col-xs-6'}),
                div_value = $('<div>', {'class': 'col-xs-6'}),
                property = $(opt.propertyElement || '<textarea>', {
                    'class': 'form-control',
                    'id': 'property',
                    'rows': 1,
                    'placeholder': gettext('Property')
                }),
                value = $(opt.valueElement || '<textarea>', {
                    'class': 'form-control',
                    'id': 'value',
                    'rows': 1,
                    'placeholder': gettext('Value')
                });

            property.val(key);
            value.val(json[key]);
            property.change({'target': target, 'opt': opt}, jsonChange);
            value.change({'target': target, 'opt': opt}, jsonChange);
            div_row.append(div_property.append(property));
            div_row.append(div_value.append(value));
            item.append(div_row).append($('<hr>'));
            target.find('.append-item').before(item);
        }
    }

    var opt = {
        change: function (data) {
            $('#id_params').val(JSON.stringify(data));
        }
    };
    $('#json-field').dictEditor(JSON.parse($('#id_params').val()), opt);

})
(jQuery);
