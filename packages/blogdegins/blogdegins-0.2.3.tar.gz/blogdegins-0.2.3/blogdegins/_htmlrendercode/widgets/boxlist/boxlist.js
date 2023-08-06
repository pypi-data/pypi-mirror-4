jQuery(function($) {
    function resize_callback(eventObject) {
        // this: dom element
        var boxlist_width;
        var section_width;

        elm = "#skills-boxlist";
        boxlist_width = $(elm).width();
        if(boxlist_width > 0) {
            var x;
            var section_width;
            x = $.scrollbarWidth();
            section_width = (boxlist_width - x)/3;
            $(".grid-container-class-33").width(section_width);
        }
    }

    $(function() {
        // Document is ready
        $(window).resize(resize_callback);
    });

    $(window).load(function () {
        resize_callback();
    });
});
