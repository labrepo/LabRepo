$(function(){
//    var $selects = $('.search-components'),
//        $searchInput = $('#id_q[type="search"]');
//    $selects.each(function(){
//        var that = $(this),
//            $parent = that.closest('.form-group'),
//            $dropDown = $(
//                '<li role="presentation" class="dropdown">' +
//                '  <a href="#" class="dropdown-toggle" data-toggle="dropdown">' + $parent.find('label').text().toLowerCase() + '</a>' +
//                '  <ul class="dropdown-menu"></ul>' +
//                '</li>'
//                ),
//            $ul = $dropDown.find('ul.dropdown-menu');
//        that.find('option').each(function(){
//            $ul.append(
//                '<li role="presentation">' +
//                '  <a href="#" class="search-elements" data-value=' + jQuery.trim($(this).val()) + '>' +
//                     jQuery.trim($(this).text()) +
//                '  </a>' +
//                '</li>');
//        });

//        $parent.hide();
//        $('ul#search-component').append($dropDown);
//    });

//    $('a.search-elements').on('click', function(e){
//        e.preventDefault();
//        var that = $(this),
//            parent = jQuery.trim(that.closest('li.dropdown').find('a.dropdown-toggle').text()),
//            searchString;
//        searchString = parent + ': {' + jQuery.trim(that.data('value')) + ': ""}';
//        $searchInput.val($searchInput.val() + ' ' + searchString);
//    });


    $('body').on('click', '.unit-checkbox', function() {
        if ($(this).prop('checked')) {
            $('form #id_units').find('option[value="' + $(this).val() + '"]').attr("selected", true);
        } else {
            $('form #id_units').find('option[value="' + $(this).val() + '"]').attr("selected", false);
        }
//        $('form #id_units').select2("val", $.map($('#unit').find('input:checked'), function(value){return $(value).val();}));
    });

    submitForm($('.create-collection-form'), function(response, form){
        showMessage(false, response.message);
        $('#modal').modal('hide');
        $('.update-experiment-form').html(response.update_collection_form);
    });
    submitForm($('.update-experiment-form'),
        function(response, form){
            showMessage(false, response.message);
            form.find('.non-field-error').empty();
        }, function(xhr, form){
            var data = xhr.responseJSON;
            form.find('.has-error').removeClass('has-error').removeAttr('title');
            for(var name in data){
                if (data.hasOwnProperty(name)){
                    var parent = form.find('[name="' + name + '"]').parents('.form-group');
                    if (parent.length && form.find('[name="' + name + '"]').is(":visible")){
                        parent.addClass('has-error').attr('title', data[name].join(', '));
                    } else {
                        form.find('.non-field-error').addClass('has-error').text(data[name].join(', '));
                    }
                }
            }
        });
});
