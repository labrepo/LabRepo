(function (factory) {
    /* global define */
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['jquery'], factory);
    } else if (typeof module === 'object' && module.exports) {
        // Node/CommonJS
        module.exports = factory(require('jquery'));
    } else {
        // Browser globals
        factory(window.jQuery);
    }
}(function ($) {

    // Extends plugins for adding filemanager.
    //  - plugin is external module for customizing.
    $.extend($.summernote.plugins, {
        /**
         * @param {Object} context - context object has status of editor.
         */
        'filemanager': function (context) {
            var self = this;

            // ui has renders to build ui elements.
            //  - you can create a button with `ui.button`
            var ui = $.summernote.ui;

            // add filemanager button
            context.memo('button.filemanager', function () {
                // create button
                var button = ui.button({
                    contents: '<i class="fa fa-cloud-upload"/>',
                    tooltip: 'Filemanager',
                    click: function () {
                        self.$panel.show();
                        self.$panel.hide(500);
                        FilemanagerDialog(context);
                    }
                });

                // create jQuery object from button instance.
                var $filemanager = button.render();
                return $filemanager;
            });

            // This method will be called when editor is initialized by $('..').summernote();
            // You can create elements for plugin
            this.initialize = function () {
                this.$panel = $('<div class="filemanager-panel"/>').css({
                    position: 'absolute',
                    width: 100,
                    height: 100,
                    left: '50%',
                    top: '50%',
                    background: 'red'
                }).hide();

                this.$panel.appendTo('body');
            };

            // This methods will be called when editor is destroyed by $('..').summernote('destroy');
            // You should remove elements on `initialize`.
            this.destroy = function () {
                this.$panel.remove();
                this.$panel = null;
            };
        }
    });
}));


window.current_summernote_context = null;

function FilemanagerDialog(context){
    $('#fm-summernote').modal('show')

    window.current_summernote_context = context;

}

//summernote image from filemanager
$('body').on('click', '#fm-summernote .fm-choose', function(e){
    var file_url = $(this).data('url')
    window.current_summernote_context.invoke('editor.insertImage', file_url);
    window.current_summernote_context = null;
    $('#fm-summernote').modal('hide')
})

window.summernote_config = {
            height: 150,
            width: '100%',
            airMode: false,
//            modules: $.extend($.summernote.options.modules, {"filemanager": Filemanager}),
            toolbar: [
                ['style', ['style']],
                ['style', ['bold', 'italic', 'underline', 'clear']],
                ['para', ['ul', 'ol']],
                ['insert', ['link', 'picture', 'filemanager']],
                ['view', ['fullscreen', 'codeview']],
                ['help', ['help']]
            ],
            keyMap: {
                pc: {
                    'CTRL+Z': 'undo',
                    'CTRL+Y': 'redo',
                    'TAB': 'tab',
                    'SHIFT+TAB': 'untab',
                    'CTRL+B': 'bold',
                    'CTRL+I': 'italic',
                    'CTRL+U': 'underline',
                    'CTRL+SHIFT+S': 'strikethrough',
                    'CTRL+BACKSLASH': 'removeFormat',
                    'CTRL+SHIFT+L': 'justifyLeft',
                    'CTRL+SHIFT+E': 'justifyCenter',
                    'CTRL+SHIFT+R': 'justifyRight',
                    'CTRL+SHIFT+J': 'justifyFull',
                    'CTRL+SHIFT+NUM7': 'insertUnorderedList',
                    'CTRL+SHIFT+NUM8': 'insertOrderedList',
                    'CTRL+LEFTBRACKET': 'outdent',
                    'CTRL+RIGHTBRACKET': 'indent',
                    'CTRL+NUM0': 'formatPara',
                    'CTRL+NUM1': 'formatH1',
                    'CTRL+NUM2': 'formatH2',
                    'CTRL+NUM3': 'formatH3',
                    'CTRL+NUM4': 'formatH4',
                    'CTRL+NUM5': 'formatH5',
                    'CTRL+NUM6': 'formatH6',
                    'CTRL+K': 'showLinkDialog'
                },

                mac: {
                    'CMD+Z': 'undo',
                    'CMD+SHIFT+Z': 'redo',
                    'TAB': 'tab',
                    'SHIFT+TAB': 'untab',
                    'CMD+B': 'bold',
                    'CMD+I': 'italic',
                    'CMD+U': 'underline',
                    'CMD+SHIFT+S': 'strikethrough',
                    'CMD+BACKSLASH': 'removeFormat',
                    'CMD+SHIFT+L': 'justifyLeft',
                    'CMD+SHIFT+E': 'justifyCenter',
                    'CMD+SHIFT+R': 'justifyRight',
                    'CMD+SHIFT+J': 'justifyFull',
                    'CMD+SHIFT+NUM7': 'insertUnorderedList',
                    'CMD+SHIFT+NUM8': 'insertOrderedList',
                    'CMD+LEFTBRACKET': 'outdent',
                    'CMD+RIGHTBRACKET': 'indent',
                    'CMD+NUM0': 'formatPara',
                    'CMD+NUM1': 'formatH1',
                    'CMD+NUM2': 'formatH2',
                    'CMD+NUM3': 'formatH3',
                    'CMD+NUM4': 'formatH4',
                    'CMD+NUM5': 'formatH5',
                    'CMD+NUM6': 'formatH6',
                    'CMD+K': 'showLinkDialog'
                }

            },
            callbacks: {
                onKeydown: function (e) {
                    if ((e.keyCode == 10 || e.keyCode == 13) && (e.ctrlKey || e.shiftKey) && !$input.summernote('isEmpty'))
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
            },
        };

function addSumernote() {
    $('.summernote').each(function (i, input) {
        var $input = $(input);
        $input.summernote(window.summernote_config)
    });
};