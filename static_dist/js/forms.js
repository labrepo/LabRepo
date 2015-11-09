$(document).ready(function () {


    addSelect2();
    addSumernote()

    submitForm($('.comment-form'), function (response, form) {
//        form.closest('.comments-block').find('div#comment').append(response.data); //old
        //if not web sockets
        form.closest('.comment-area').find('.comments-list').append(response.data);  // new

        $('div#all div.resent-activities ul:not(.pager), div#comments_activities div.resent-activities ul:not(.pager)').prepend(response.resent_activity);
        form.trigger('reset').find('.has-error').removeClass('has-error');
        var comment_field_id = form.find('textarea[name="create-text"]').attr('id');
        $('#' + comment_field_id).code('');
//        CKEDITOR.instances[comment_field_id].setData('');
//        CKEDITOR.instances[comment_field_id].setData('');
    });

    // Scroll to comment's block bottom
    if ($(".comment-activities").length) {
        $(".comment-activities").scrollTop($(".comment-activities")[0].scrollHeight);
    }

    // Add lightbox to chat images
    $('.comment-block .comment-text img').each(function (i, element) {
        var that = $(element)
        that.wrap( '<a href="'+that.attr('src')+'" data-lightbox="'+ i +'"></a>' );
    });


    invite();

    $('body')
        .on('click', '.comment-edit', function (e) {
            var that = $(this),
                value = that.closest('.comment-block').find('.comment-context').html();

            $('div.comment-modal form').attr('action', that.data('url')).find('[name="update-text"]').val(value);
            var comment_field_id = that.closest('.comment-area').find('div.comment-modal textarea[name="update-text"]').attr('id');
            $(that.closest('.comment-area').find('div.comment-modal textarea[name="update-text"]')).code(value);
//            CKEDITOR.instances[comment_field_id].setData(value);
        })
        .on('click', '.comment-remove', function () {
            submitForm($(this).closest('form'), function (response) {
                $('div[data-pk="' + response.pk + '"]').remove();
                $('.confirm-delete-comment').modal('hide');
            });
        });

    submitForm($('div.comment-modal form'), function (response) {
        $('div[data-pk="' + response.pk + '"]').replaceWith(response.data);
        $('.comment-modal').modal('hide');
    });

    $('body').on('click','.description-edit', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(e.target).parents('.description-show').hide().parents('#description').find('.description-editor').show();
    });
    $('body').on('click','.cancel-edit', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(e.target).parents('.description-editor').hide().parents('#description').find('.description-show').show();
    });

    $('body').on('click','.field-edit', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(e.target).closest('.field-show').hide().closest('.field-container').find('.field-editor').show();
    });
    $('body').on('click','.cancel-edit', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(e.target).closest('.field-editor').hide().closest('.field-container').find('.field-show').show();
    });
});

function addSumernote() {
    $('.summernote').each(function (i, input) {
        var $input = $(input);
        $input.summernote({
            height: 150,
            width: '100%',
            airMode: false,
            focus: true,
            toolbar: [
                ['style', ['style']],
                ['style', ['bold', 'italic', 'underline', 'clear']],
                ['para', ['ul', 'ol']],
                ['insert', ['link', 'picture']],
                ['view', ['fullscreen', 'codeview']],
                ['help', ['help']]
            ],
            onKeydown: function (e) {
                if (e.keyCode == 13 && e.shiftKey && !$input.summernote('isEmpty'))
                {
                    $input.closest('form').submit()
                    // prevent default behavior
                    e.preventDefault();
                }
            },

            onImageUpload: function(files) {
                var imageInput = $('.note-image-input');
                var sn = $(this);
                imageInput.fileupload({
                    uploadTemplateId: null,
                    downloadTemplateId: null,
                });

                var jqXHR = imageInput.fileupload('send',
                    {
                        files: files,
                        formData: {csrfmiddlewaretoken: csrftoken},
                        url: '/' + lab_pk + '/filemanager/summernote_upload/',
                    })
                    .success(function (data, textStatus, jqXHR) {
                        $.each(data.files, function (index, file) {
                            sn.summernote("insertImage", file.url);
                        });
                    })
                    .error(function (jqXHR, textStatus, errorThrown) {
                        // TODO: Display a detailed error message. It will come from JSON.
                        alert( 'Got an error while uploading images.' );
                    });
            }
        });
        //fix started bug
        $input.code('');
    });
};

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

//$('#confirm-delete,#confirm-delete-comment').on('show.bs.modal', function (e) {
//    $(this).find('#formConfirmDelete').attr('action', $(e.relatedTarget).data('href'));
//});

$('body').on('click', '.comment-delete', function (e) {
    $('.formConfirmDelete').attr('action', $(e.target).closest('button').data('href'));
});

function submitForm(el, callback, error_callback) {
    $('body').on('submit', el.selector, function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();

        var $form = $(e.target);

        if (typeof CKEDITOR !== "undefined") {
            for (var instance in CKEDITOR.instances) {
                if (CKEDITOR.instances.hasOwnProperty(instance)) {
                    CKEDITOR.instances[instance].updateElement();
                }
            }
        }

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
    $('select.select2').each(function (i, input) {
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

function form_fail($form, xhr) {
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

