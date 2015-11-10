$('.sidebar-toggle').click(function (event) {
    if ($('body').hasClass('sidebar-collapse')) {
        Cookies.remove("sidebarcollapse");
    } else {
        Cookies.set("sidebarcollapse", 1);
    }
})


// -----  Dashboard  -----
$('body').on('submit','.storage-add', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var $form = $(e.target);
    $.post($form.attr('action'), $form.serialize())
      .fail(function (xhr) {
          form_fail($form, xhr)
      }).done(function (response) {
        location.reload();
      });
  });

  $('body').on('click','.storage-show-more', function (e) {
    e.preventDefault();
    e.stopPropagation();
    $('.storage-more').toggle();
  });

  $('body').on('click','.storage-edit', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var that = $(this);
    $.get(that.data('url'),{})
            .fail(function (xhr) {
              form_fail($form, xhr)
            }).done(function (response) {
              $('.storage').find('.storage-form-area').hide()
              $('.storage-add').hide()
              $('.storage').find('.list-group-item').show()
              that.closest('.storage').find('.storage-form-area').show().html(response.form_html)
              that.closest('.storage').find('.list-group-item').hide()
            });
  });

  $('body').on('click','.storage-edit-cancel', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var that = $(this);
    that.closest('.storage').find('.storage-form-area').hide()
    $('.storage-add').show()
    that.closest('.storage').find('.list-group-item').show()
  });

  //  $('body').on('submit','.storage-edit-form', function (e) {
  //    e.preventDefault();
  //    e.stopPropagation();
  //    var $form = $(e.target);
  //    $.post($form.attr('action'), $form.serialize())
  //      .fail(function (xhr) {
  //          form_fail($form, xhr)
  //      }).done(function (response) {
  //        location.reload();
  //      });
  //  });

  $('body').on('click','.storage-delete', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var that = $(this);
    if (confirm("Remove storage")) {
      $.post(that.data('url'),{})
              .fail(function (xhr) {
                form_fail($form, xhr)
              }).done(function (response) {
                that.closest('.storage').remove()
              });
    } else {
      return false
    }
  });
