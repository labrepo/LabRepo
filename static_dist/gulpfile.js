var
    gulp = require('gulp'),
    concat = require('gulp-concat'),
    filter = require('gulp-filter'),
    mainBowerFiles = require('main-bower-files'),
    runSequence = require('run-sequence'),
    print = require('gulp-print'),
    uglify = require('gulp-uglify'),
    minifyCss = require('gulp-minify-css'),
    urlAdjuster = require('gulp-css-url-adjuster'),
    addsrc = require('gulp-add-src')
    ;

gulp.task('default', function (callback) {
    runSequence(
        'styles:vendor',
        'scripts:jquery',
        'scripts:vendor',
        'copy_fonts',
        'copy_templates',
        'images:vendor',
        'images:app',
        'scripts:app',
        'styles:app',

        function (error) {
            if (error) {
                console.log(error.message);
            } else {
                console.log('RELEASE FINISHED SUCCESSFULLY');
            }
            callback(error);
        });
});

gulp.task('images:vendor', function() {
    return gulp.src(mainBowerFiles({
        "overrides":{
            "jstree":{
                "main": [
                    "./dist/themes/default/32px.png",
                    "./dist/themes/default/40px.png",
                    "./dist/themes/default/throbber.gif",
                ]
            }

        }
    }))
        .pipe(addsrc([
            'bower_components/AdminLTE/dist/img/**',
            'bower_components/AdminLTE/plugins/colorpicker/img/**',
            'bower_components/blueimp-file-upload/img/**'
        ]))
        .pipe(filter([
            '**/*.{png,gif,svg,jpeg,jpg}',
        ]))
        .pipe(gulp.dest('../static/images/'));
});


gulp.task('styles:vendor', function () {
    return gulp.src(
        [
            "bower_components/AdminLTE/bootstrap/css/bootstrap.min.css",
            "bower_components/select2/select2.css",
            "bower_components/select2/select2-bootstrap.css",
            "bower_components/font-awesome/css/font-awesome.min.css",
            "bower_components/Ionicons/css/ionicons.min.css",
            "static_libs/AdminLTE.css", //fix image width in a chat
            "bower_components/AdminLTE/dist/css/skins/skin-black.min.css",
            "bower_components/handsontable/dist/handsontable.full.min.css",
            "bower_components/handsontable/plugins/bootstrap/handsontable.bootstrap.css",
            "bower_components/AdminLTE/plugins/fullcalendar/fullcalendar.min.css",
            "bower_components/AdminLTE/plugins/colorpicker/bootstrap-colorpicker.min.css",
            "bower_components/jstree/dist/themes/default/style.min.css",
            "bower_components/jquery.fancytree/dist/skin-bootstrap/ui.fancytree.min.css",
            "bower_components/summernote/dist/summernote.css",
            "bower_components/lightbox2/dist/css/lightbox.css",
            "bower_components/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css",
            "bower_components/blueimp-gallery/css/blueimp-gallery.min.css",
            "bower_components/blueimp-file-upload/css/jquery.fileupload.css",
            "bower_components/blueimp-file-upload/css/jquery.fileupload-ui.css",
            "bower_components/blueimp-file-upload/css/jquery.fileupload-ui-noscript.css",

            // custom plugins or modified files
            "static_libs/angular-filemanager/dist/animations.css",
            "static_libs/angular-filemanager/dist/dialogs.css",
            "static_libs/angular-filemanager/dist/main.css",
        ])
        .pipe(concat('vendors.css'))
        .pipe(urlAdjuster({
            replace:  ['select2-spinner.gif','../images/select2-spinner.gif'],
        }))
        .pipe(urlAdjuster({
            replace:  ['select2.png','../images/select2.png'],
        }))
        .pipe(urlAdjuster({
            replace:  ['select2x2.png','../images/select2x2.png'],
        }))
        .pipe(urlAdjuster({
            replace:  ['32px.png','../images/32px.png'],
        }))
        .pipe(urlAdjuster({
            replace:  ['40px.png','../images/40px.png'],
        }))
        .pipe(urlAdjuster({
            replace:  ['throbber.gif','../images/throbber.gif'],
        }))
        .pipe(urlAdjuster({
            replace:  ['../',''],

        }))
        .pipe(urlAdjuster({
            replace:  ['img/','images/'],
        }))
        .pipe(minifyCss({processImport: false}))
        .pipe(gulp.dest('../static/'));
})

gulp.task('copy_fonts', function () {

    return gulp.src([
        "bower_components/bootstrap/fonts/**",
        "bower_components/font-awesome/fonts/**",
        "bower_components/Ionicons/fonts/**",
    ])
        .pipe(gulp.dest('../static/fonts/'));
})


gulp.task('copy_templates', function () {
  return gulp.src([
        "static_libs/angular-filemanager/src/templates/**.html",
    ])
        .pipe(gulp.dest('../static/src/templates/'));
})

gulp.task('scripts:jquery', function () {
    return gulp.src([
        "bower_components/jquery/dist/jquery.min.js",
    ])
    .pipe(gulp.dest('../static/'));
})

gulp.task('scripts:vendor', function () {

    return gulp.src([
        "bower_components/jquery-ui/jquery-ui.min.js",
        "bower_components/js-cookie/src/js.cookie.min.js",
        "bower_components/bootstrap/dist/js/bootstrap.min.js",
        "bower_components/moment/min/moment.min.js",
        "bower_components/angular/angular.min.js",
        "bower_components/angular-cookies/angular-cookies.min.js",
        "bower_components/angular-translate/angular-translate.min.js",
        "bower_components/AdminLTE/dist/js/app.js",
        "bower_components/AdminLTE/plugins/slimScroll/jquery.slimscroll.min.js",
        "bower_components/AdminLTE/plugins/fullcalendar/fullcalendar.min.js",
        "bower_components/AdminLTE/plugins/colorpicker/bootstrap-colorpicker.min.js",
        "bower_components/blueimp-tmpl/js/tmpl.min.js",
        "bower_components/blueimp-load-image/js/load-image.all.min.js",
        "bower_components/blueimp-canvas-to-blob/js/canvas-to-blob.min.js",
        "bower_components/blueimp-file-upload/js/jquery.iframe-transport.js",
        "bower_components/blueimp-gallery/js/blueimp-gallery.min.js",
        "bower_components/blueimp-file-upload/js/jquery.fileupload.js",
        "bower_components/blueimp-file-upload/js/jquery.fileupload-ui.js",
        "bower_components/blueimp-file-upload/js/jquery.fileupload-process.js",
        "bower_components/blueimp-file-upload/js/jquery.fileupload-validate.js",
        "bower_components/d3/d3.min.js",
        "bower_components/webcola/WebCola/cola.min.js",
        "bower_components/eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js",
        //"bower_components/angular-filemanager/dist/angular-filemanager.min.js",
        "bower_components/pikaday/pikaday.js",
        "bower_components/zeroclipboard/dist/ZeroClipboard.js",
        "bower_components/jquery.fancytree/dist/jquery.fancytree-all.min.js",
        "bower_components/jstree/dist/jstree.min.js",
        "bower_components/lightbox2/dist/js/lightbox.min.js",
        "bower_components/select2/select2.min.js",
        "bower_components/summernote/dist/summernote.min.js",

        // custom plugins or modified files
        "static_libs/blueimp-uploader/locale.js",
//        "static/datetimepicker/js/bootstrap-datetimepicker.min.js",
        "static_libs/jquery-handsontable/jquery.handsontable.full.js",
        "static_libs/jquery-handsontable/selectMultipleEditor.js",
        "static_libs/jquery-handsontable/select2Editor.js",
        "static_libs/jquery-handsontable/jsTreeEditor.js",
        "static_libs/jquery-handsontable/datetimeEditor.js",
        "static_libs/angular-filemanager/dist/angular-filemanager.min.js"
    ])
        .pipe(concat('vendors.js'))
        .pipe(uglify())
        .pipe(gulp.dest('../static/'));
})

gulp.task('scripts:app', function () {

    return gulp.src([
        "js/**.js",
    ])
        .pipe(concat('app.js'))
        .pipe(uglify())
        .pipe(gulp.dest('../static/'));
})

gulp.task('styles:app', function () {

    return gulp.src([
        "css/**.css",
    ])
        .pipe(concat('styles.css'))
        .pipe(minifyCss({processImport: false}))
        .pipe(gulp.dest('../static/'));
})

gulp.task('images:app', function() {
    return gulp.src([
        "img/**",
    ])
        .pipe(filter([
            '**/*.{png,gif,svg,jpeg,jpg}',
        ]))
        .pipe(gulp.dest('../static/img/'));
});