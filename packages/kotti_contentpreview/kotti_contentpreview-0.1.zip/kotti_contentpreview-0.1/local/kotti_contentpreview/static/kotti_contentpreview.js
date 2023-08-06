$(function() {

    // only run if we are in the @@contents view
    if(/@@contents$/.test(document.location.href)) {
        // collect the settings from the server
        var view_name = '@@view';
        var window_size = '50%';
        var delay_show = 500;
        var delay_hide = 750;
        $.ajax({
            async: false,
            url: '/@@contentpreview_settings',
            success: function(response) {
                view_name = response['view_name'];
                window_size = response['window_size'];
                delay_show = response['delay_show'];
                delay_hide = response['delay_hide'];
            }
        });
        // set up the popover with the content of the defined view
        var popover = $('#contents-table td:nth-child(2) a').popover({
            html: true,
            trigger: 'hover',
            delay: { show: delay_show, hide: delay_hide },
            content: function() {
                var div_id =  "div-id-" + $.now();
                var link = $(this).attr('href');
                link = link.replace('@@contents', view_name);
                $.ajax({
                    url: link,
                    success: function(response) {
                        $('#' + div_id).html(response);
                    }
                });
                return '<div id="'+ div_id +'">Loading...</div>'
            }
        });
        // set the width for the popover after it is shown
        popover.bind("shown", function(evt) {
            var popo_div = $('.popover', $(this).parent());
            popo_div.css('width', window_size);
            popo_div.css('max-width', window_size);
        });
    };
});
