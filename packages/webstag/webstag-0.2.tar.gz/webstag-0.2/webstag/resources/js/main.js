$(function() {

    var options = {
        slideshow: true,
        slideshowAuto: false,
        // Store the image number in the URL fragment
        onLoad: function() {
            var index = $(this).parent().prevAll().length;
            window.location.hash = index + 1;
        },
        onClosed: function() {
            window.location.hash = 'all';
        }
    }

    // photos
    $("li.photo a.thumbnail").colorbox(options);
    // videos
    $("li.video a.thumbnail").each(function() {
        $(this).colorbox($.extend({}, options,
                         { iframe: true,
                           innerWidth: $(this).attr("data-width"),
                           innerHeight: $(this).attr("data-height")
                         }));
    });

    // Display the element specified in the URL fragment
    if (window.location.hash) {
        var num = parseInt(window.location.hash.replace(/[^0-9]/, '')) - 1;
        $("li a.thumbnail").eq(num).click();
    }


});
