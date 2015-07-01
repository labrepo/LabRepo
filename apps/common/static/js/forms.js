$(document).ready(function () {
    addSelect2();

    submitForm($('#comment-form'), function (response, form) {
        $('div#comment').append(response.data);
        $('div#all div.resent-activities ul:not(.pager), div#comments_activities div.resent-activities ul:not(.pager)').prepend(response.resent_activity);
        form.trigger('reset').find('.has-error').removeClass('has-error');
        CKEDITOR.instances['id_create-text'].setData('');
    });

    invite();

    $('#comment')
        .on('click', '.comment-edit', function () {
            var that = $(this),
                value = that.closest('.input-group.margin').find('.comment-context').html();
            $('div#comment-modal form').attr('action', that.data('url')).find('[name="update-text"]').val(value);
            CKEDITOR.instances['id_update-text'].setData(value);
        })
        .on('click', '.comment-remove', function () {
            submitForm($(this).closest('form'), function (response) {
                $('div[data-pk="' + response.pk + '"]').remove();
                $('#confirm-delete-comment').modal('hide');
            });
        });

    submitForm($('div#comment-modal form'), function (response) {
        $('div[data-pk="' + response.pk + '"]').replaceWith(response.data);
        $('#comment-modal').modal('hide');
    });

    $('.description-edit').click(function (e) {
        e.preventDefault();
        $(this).parents('.description-show').hide().parents('#description').find('.description-editor').show();
    });
    $('.cancel-edit').click(function (e) {
        e.preventDefault();
        $(this).parents('.description-editor').hide().parents('#description').find('.description-show').show();
    });

});

function invite() {
    submitForm($('.invite-member'), function (response, form) {
        var fields = form.data('field').split(',');
        for (var i = 0, max = fields.length; i < max; i += 1) {
            var $select = $('[name="' + fields[i] + '"]'),
                option = new Option(response.name, response.pk, false, false),
                values = $select.select2('val');
            $select.append(option).select2('val', values).select2('close');
        }
        $('[id^="modal"]').modal('hide');
    });
}

$('#confirm-delete,#confirm-delete-comment').on('show.bs.modal', function (e) {
    $(this).find('#formConfirmDelete').attr('action', $(e.relatedTarget).data('href'));
});

function submitForm(el, callback, error_callback) {
    el.submit(function (e) {
        e.preventDefault();
        var $form = $(this);
        if (typeof CKEDITOR !== "undefined") {
            for (var instance in CKEDITOR.instances) {
                if (CKEDITOR.instances.hasOwnProperty(instance)) {
                    CKEDITOR.instances[instance].updateElement();
                }
            }
        }
        console.log($form);
        $.post($form.attr('action'), $form.serialize())
            .fail(function (xhr) {
                if (error_callback) {
                    error_callback(xhr, $form);
                }
                else {
                    var data = xhr.responseJSON;
                    $form.find('.has-error').removeClass('has-error').removeAttr('title');
                    for (var name in data) {
                        if (data.hasOwnProperty(name)) {
                            var icon = $('<i>', {'class': 'fa fa-warning'}),
                                error_message = $('span', {
                                    'class': 'text-red error-msg',
                                    'id': 'error_' + $form.find('[name="' + name + '"]').id
                                }).text(data[name].join(', ')).append(icon);

                            $form.find('[name="' + name + '"]')
                                .after(error_message);
                            $form.find('[name="' + name + '"]')
                                .parents('.form-group')
                                .addClass('has-error')
                                .attr('title', data[name].join(', '));
                        }
                    }
                }
            }).done(function (response) {
                callback(response, $form);
            });
    });
}

function showMessage(hasError, messages) {

    var baseMessages = $('#messages').find('.alert'),
        divClass = hasError ? 'alert-danger' : 'alert-success',
        iClass = hasError ? 'fa-ban' : 'fa-check',
        bText = hasError ? gettext('Error!') : gettext('Success!'),
        message = $('<div>', {'class': 'alert alert-dismissable ' + divClass})
        .append($('<i>', {'class': 'fa ' + iClass}))
        .append($('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'))
        .append($('<b>').html(bText))
        .append($('<p>').html(messages))
        .fadeIn();

    baseMessages.length !== 0 ? baseMessages.first().before(message) : message.appendTo('#messages')
}


function addSelect2() {
    $('.select2').each(function (i, input) {
        var $input = $(input);
        $input.find('option[selected="selected"]').each(function (e) {
            var $option = $(this),
                dependent = $input.data('dependent') || '';
            dependent.split(',').forEach(function (name) {
                $('[name="' + name + '"].select2').find('option[value=' + $option.val() + ']').attr('disabled', 'disabled');
            });
        });
        $input.select2()
            .on("select2-removed", function (e) {
                var dependent = $input.data('dependent') || '';
                dependent.split(',').forEach(function (name) {
                    $('[name="' + name + '"].select2').find('option[value=' + e.val + ']').removeAttr('disabled');
                });
            }).on("select2-selecting", function (e) {
                var dependent = $input.data('dependent') || '';
                dependent.split(',').forEach(function (name) {
                    $('[name="' + name + '"].select2').find('option[value=' + e.val + ']').attr('disabled', 'disabled');
                });
            });
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
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
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
