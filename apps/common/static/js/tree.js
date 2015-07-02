
$(function () {
    InitJSTree($('#location-tree'));
});

function InitJSTree(treeElement, plugins){

        if (typeof(treeElement)==='undefined') treeElement = $('#location-tree');
        if (typeof(plugins)==='undefined') plugins = ['search'];

        searchElement = $('#search'),
        formContainerElement = $('#location-container'),
        formElement = '#location-form',
        tree = treeElement
            .on('changed.jstree', function (e, data) {
                e.preventDefault();
                if (data.selected && data.action === 'select_node') {
                    var instance = data.instance.get_node(data.selected[0]);
                    if (instance.a_attr.href != '#') {
                        $.get(instance.a_attr.href)
                            .done(function (response) {
                                formContainerElement.html(response);
                                addSelect2();
                                var $form = formContainerElement.find(formElement),
                                    $plot = $('#plot');
                                submitForm($form,
                                    function (response) {
                                        var node = response.node;
//                                        for (var i = 0, max = node.length; i < max; i += 1) {
//                                            treeElement.jstree('rename_node', treeElement.jstree('get_node', node[i].id), node[i].text);
//                                        }
                                        treeElement.jstree(true).delete_node(instance);
                                        for (var i = 0, max = node.length; i < max; i += 1) {
                                            treeElement.jstree(true).create_node(
                                                data.instance.get_node(node[i].parent),
                                                node[i], 'last', false, true
                                            );
                                        }
                                        $form.find('.has-error').removeClass('has-error');
                                        showMessage(false, response.message);
                                    });
                                invite();

                                if ($plot.length) {
                                    $('select#measurement_type').on('change', function () {
                                        $.get($(this).find('option:selected').data('url')).done(function (response) {
                                            $plot.html(response.plot);
                                        });
                                    });
                                }
                            }).fail(function (xhr) {
                                showMessage(true, xhr.responseJSON);
                                console.log(xhr.responseJSON);
                            });
                    } else {
                        formContainerElement.html('');
                    }
                }
            })
            .jstree({
                'core': {
                    'animation': 0,
                    'check_callback': true,
                    'themes': {'stripes': true},
                    'data': treeElement.data('content')
                },
                'search': {
                    show_only_matches: true
                },
                'checkbox': {
                    three_state: false,
                },
                'plugins': plugins
            }),
        to = false;

    searchElement.keyup(function () {
        if (to) {
            clearTimeout(to);
        }
        to = setTimeout(function () {
            var v = searchElement.val();
            tree.jstree(true).search(v);
        }, 250);
    });

    $('#location-create').click(function (e) {
        var selected_node = tree.jstree(true).get_selected(),
            parent_node = $('#' + selected_node).closest('[data-create-url]'),
            url = parent_node.data('create-url');

        $.get((url || $(this).data('url')) + '?parent=' + selected_node)
            .done(function (response) {
                formContainerElement.html(response);
                addSelect2();
                var $form = formContainerElement.find(formElement);
                submitForm($form,
                    function (response) {
                        var node = response.node;
                        for (var i = 0, max = node.length; i < max; i += 1) {
                            treeElement.jstree(true).create_node(
                                treeElement.jstree(true).get_node(node[i].parent),
                                node[i], 'last', false, true
                            );
                        }
                        $form.trigger('reset').find('.has-error').removeClass('has-error');
                        $('.select2').select2('data', null);
                        showMessage(false, response.message);
                    });
                invite();
            }).fail(function (xhr) {
                showMessage(true, xhr.responseJSON);
                console.log(xhr.responseJSON);
            });
    });

    $('#location-remove').click(function (e) {
        e.preventDefault();
        var selected_node = treeElement.jstree('get_selected'),
            url = $('#' + selected_node).closest('[data-remove-url]').data('remove-url');
        $.post(url || $(this).closest('form').attr('action'), {
            ids: selected_node,
            csrfmiddlewaretoken: csrftoken
        }).done(function (response) {
            treeElement.jstree(true).delete_node(selected_node);
            formContainerElement.html('');
            showMessage(false, response.message);
        }).fail(function (xhr) {
            showMessage(true, xhr.responseJSON);
            console.log(xhr.responseJSON);
        });
        $('#confirm-delete').modal('hide');
    });
    $(document).bind("click", function (e) {
        if ($(e.target).parents(".left-side").length || $(e.target).parents('header').length) {
            treeElement.jstree(true).deselect_all();
            formContainerElement.html('');
        }
    });
}