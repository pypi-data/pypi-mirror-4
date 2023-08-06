(function($) {
    $(document).ready(function() {
        var start_slideshow_buttons = $(".xhostplusGalleryContent .xhostplusGalleryStartSlideshow");

        var slideshow_interval_time = parseInt($("#xhostplus_gallery_slideshow_interval").html()) * 1000;
        var slideshow_interval = null;

        var gallery_elements = $(".xhostplusGalleryContent .photoAlbumEntry a").not(".xhostplusGalleryContent .photoAlbumFolder a");
        var portlet_elements = $(".portletGallery .portletItem a");
        var zoomable_elements = $(".xhostplusGalleryImageZoom a").add($(".xhostplusGalleryImageZoom").parents("a"));

        zoomable_elements.xhostplusbox({
            'titleShow'     : true,
            'transitionIn'  : 'elastic',
            'transitionOut' : 'elastic'
        });

        gallery_elements.xhostplusbox({
            'titleShow'     : true,
            'transitionIn'  : 'elastic',
            'transitionOut' : 'elastic',
            'cyclic'        : true,
            'onClosed'      : function() {
                if(slideshow_interval)
                    window.clearInterval(slideshow_interval);
                slideshow_interval = null;
                $("#xhostplusbox-left, #xhostplusbox-right").css({
                    'visibility' : 'visible'
                });
            }
        });

        portlet_elements.xhostplusbox({
            'titleShow'     : true,
            'transitionIn'  : 'elastic',
            'transitionOut' : 'elastic'
        });

        start_slideshow_buttons.click(function() {
            $("#xhostplusbox-left, #xhostplusbox-right").css({
                'visibility' : 'hidden'
            });
            gallery_elements.eq(0).trigger('click');
            slideshow_interval = window.setInterval($.xhostplusbox.next, slideshow_interval_time);
            return false;
        });
    });
})(jQuery);
