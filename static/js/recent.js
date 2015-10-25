$(document).ready(function() {
    var $tabContainer = $('div.tab-pane[data-url]');
    $tabContainer.each(function(){
        var that = $(this);
        $.get(that.data('url')).done(function(response){
            that.html(response);
        });
    }).on('click', 'ul.pager a', function(e){
        e.preventDefault();
        var that = $(this);
        if (that.attr('href').length) {
            $.get(that.attr('href')).done(function (response) {
                $tabContainer.filter('.active').html(response);
            });
        }
        return false;
    })
});
