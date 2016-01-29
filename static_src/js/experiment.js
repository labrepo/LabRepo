var exp_pk = $("#experiment_row").data('experiment-pk');
window.unit_pk = null;


function show_workfow() {
    $('#workflow').html(
        '<div class="row"><div class="col-lg-12"><div style="overflow:hidden">' +
        '<iframe src="http://wooflo.magic60.ru/project/' + wooflo_key + '" width="100%" height="100%">' +
        'Your browser doesn\'t support iframes' +
        '</iframe></div></div></div>'
    );
}

$(function() {

    // fix bootstrap tabs urls
    var hash = window.location.hash;
    hash = hash.substr(0, 2) == '#/' ? '#' + hash.substr(2) :  hash;
    hash && $('ul.nav a[href="' + hash + '"]').tab('show');

    $('.nav-tabs.exp-nav a').click(function (e) {
        $(this).tab('show');
        var scrollmem = $('body').scrollTop();
        window.location.hash = this.hash;
        $('html,body').scrollTop(scrollmem);
    });

    // fix d3 in hidden tabs
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        window.dispatchEvent(new Event('resize'));
    })
    if ($('.graph-area').length){
        var graph = window.graph  = new render_graph($('.graph-area').data('graph-json'), '.graph-area', update_unit_info_ang)
    }

    $('.show-workflow').one('click', function(e) {
      show_workfow()
    });
    if (hash == '#workflow') {
        show_workfow()
    }

});

function update_unit_info_ang(unit){
    var scope = angular.element($("#unit-page")).scope();
    scope.$apply(function(){
        scope.getUnit(unit.id);
    });
    update_unit_info(unit)
}

$('.unit-item').click(function (e) {  //todo
    e.preventDefault();
    e.stopPropagation();
    var unit_id = $(this).data('unit-pk');
    update_unit_info({id: unit_id});
});

function update_unit_info(unit){
    /**
     * Update unit info tabs.
     * @param unit - object {id: unit_id} For the the compatibility with d3 function call.
     */

    var url = '/' + lab_pk + '/units/detail_json/'+ unit.id + '/'
    $.get(url, {unit_pk: unit.id}, function(unit_data){

        // set global current unit
        window.unit_pk = unit_data.pk

        // Uploader
        $('.upload-area').html(unit_data.uploader)
        update_uploaders()

        options = {
            success: function(files) {
                var url = '/' + lab_pk + '/units/'+ unit_data.pk +'/dropxbox-upload/'
                var need_upload = $('.upload-file').is(":checked")
                $.post(url,{'files[]': JSON.stringify(files), 'need_upload': need_upload}, function(data){
                    $('.blueimp-uploader').fileupload('destroy');
                    $('.blueimp-uploader').find('.file_table').html("");
                    update_uploaders()
                })
            },
            cancel: function() {},
            linkType: "direct",
            multiselect: true,
            //    extensions: ['.pdf', '.doc', '.docx'],
        };

        var button = Dropbox.createChooseButton(options);
        document.getElementById("dropbox").appendChild(button);

    });
}

// fix handsontable bug with tabs
$('a[href="#unit-measurements"]').on('shown.bs.tab', function (e) {
    if ($('#unit-measurements .btn').is(':visible')) {
        $('#dataTableEditable').handsontable('render');
    }
});


//upload files from filemanager
$('body').on('click', '#fm .fm-choose', function(e){
    var file_url = $(this).data('path')
    var file_name = $(this).data('name');

    var url = '/' + lab_pk + '/units/'+ window.unit_pk +'/local-upload/'
    var need_upload = $('.upload-file').is(":checked")
    var file = {
        name:file_name,
        link:file_url,
    }
    $.post(url,{'files[]': JSON.stringify([file,]), 'need_upload': need_upload}, function(data){
        $('.blueimp-uploader').fileupload('destroy');
        $('.blueimp-uploader').find('.file_table').html("");
        update_uploaders()
    })
    $('#fm').modal('hide')
})

//$('.box-comments').scroll(function (e) {
//    if($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
//        $('.comments-alert').hide(1000)
//        var url = $('#experiment_row').data('read-url')
//        $.post(url, {'comment': $('.box-comment').last().data('pk')})
//    }
//});


// set height of comment block
//    $('.comment-activities').css('max-height', window.innerHeight -430)
//    var sidebar_height = $('.main-sidebar').height();
//    if (window.innerHeight > 650) {
//        $('.comment-activities').not('.comments-list').css('max-height', sidebar_height - 325).css('min-height', sidebar_height - 325);
//        console.log($('.comment-activities').not('.comments-list'))
//        console.log($('.comment-activities'))
//    }
//    if ($('#exp-workfow iframe').length) {
//        $('#exp-workfow iframe').css('min-height', sidebar_height - 100)
//        setTimeout(function () {
//            comments_scroll_to_end()
//        }, 500);
//    }