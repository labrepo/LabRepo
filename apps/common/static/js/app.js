$('.sidebar-toggle').click(function (event) {
    if ($('body').hasClass('sidebar-collapse')) {
        Cookies.remove("sidebarcollapse");
    } else {
        Cookies.set("sidebarcollapse", 1);
    }
})
