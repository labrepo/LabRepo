$('.sidebar-toggle').click(function (event) {
    if ($('body').hasClass('sidebar-collapse')) {
        Cookies.remove("sidebarcollapse");
    } else {
        Cookies.set("sidebarcollapse", 1);
    }
})

// -----  MathJax  -----
window.MathJax.Hub.Config({
    displayAlign: "left"
});
window.MathJax.Hub.Configured()

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

// -----  Color widget  -----
 $(function() {
     $(".input-colorpicker").colorpicker();
 });


// -----  Datetime picker  -----
(function ($) {
    $('.datetimepicker-container').datetimepicker({
        locale: document.getElementsByTagName("html")[0].getAttribute("lang")
    });
})(jQuery);


//function comments_scroll_to_end(a) {
//    $(".comments-block").scrollTop($(".comments-block")[0].scrollHeight);
//};
