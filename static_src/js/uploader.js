$(function () {
    update_uploaders()

});

function update_uploaders() {

    //disable default browser drop & dragover actions
    $(document).bind('drop dragover', function (e) {
        e.preventDefault();
    });

    //UPLOADER

    'use strict';
    // Initialize the jQuery File Uploud
    var $uploaders = $('.blueimp-uploader');
    if ($uploaders.length) {
        $uploaders.each(function () {
            var $uploader = $(this);
            var uploadUrl = $uploader.data('upload-url');
            if ($uploader.data('mimetypes')) {
                var acceptFileTypes = $uploader.data('mimetypes');
            } else {
                var acceptFileTypes =  /.*$/i; //TODO: this
            }
            var maxNumberOfFiles = $uploader.data('maxfiles');
            var showUploaded = $uploader.data('show-uploaded');

            $uploader.fileupload({
                url: uploadUrl,
                paramName: 'file',
                autoUpload: true,
                acceptFileTypes: acceptFileTypes,
                dropZone: $uploader,
//                        maxFileSize: 50000000, // 50MB
                maxNumberOfFiles: maxNumberOfFiles,

                messages: {
                    maxNumberOfFiles: 'Превышен лимит числа файлов',
                    acceptFileTypes: 'Запрещённый тип файла',
                    maxFileSize: 'Размер файла больше разрешённого',
                    minFileSize: 'Размер файла меньше разрешённого'
                }
            });
            $uploader.addClass('fileupload-processing');
            $.ajax({
                url: $uploader.fileupload('option', 'url'),
                dataType: 'json',
                context: $uploader[0]
            }).always(function () {
                $(this).removeClass('fileupload-processing');
            }).done(function (result) {
                $(this).fileupload('option', 'done')
                    .call(this, $.Event('done'), {result: result});
            });
        });
    }
}