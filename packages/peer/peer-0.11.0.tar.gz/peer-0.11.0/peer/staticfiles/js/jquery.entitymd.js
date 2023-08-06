(function( $ ){

    $.fn.entitymd = {};  // namespace

    $.fn.entitymd.get_metadata = function() {
        var title = $(this).attr('title');
        var url = $(this).attr('href') + " table";
        $('div#metadata-contents').load(url, function () {
            $(this).dialog({
                width: 800,
                height: 400,
                title: title,
                buttons: {
                    'Close': function() { $(this).dialog("close"); }
                }
            });
        });

        return false;
    };

    $.extend($.ui.dialog.defaults, {
        overlay : {opacity: 1.0},
        modal: true
    });

})( jQuery );
