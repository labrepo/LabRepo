$(document).ready(function() {
    var $tabContainer = $('div.tab-pane[data-url]');
    $tabContainer.each(function(){
        var that = $(this);
        $.get(that.data('url')).done(function(response){
            that.html(response);
            set_recent_height();
        });
    }).on('click', 'ul.pager a', function(e){
        e.preventDefault();
        var that = $(this);
        if (that.attr('href').length) {
            $.get(that.attr('href')).done(function (response) {
                $tabContainer.filter('.active').html(response);
                set_recent_height();
            });
        }
        return false;
    })
});

function set_recent_height() {
    $('#timelineDiv').slimScroll({
        height: '510px'
    });
};