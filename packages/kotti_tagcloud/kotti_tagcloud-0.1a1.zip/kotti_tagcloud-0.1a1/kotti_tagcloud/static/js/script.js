/* Put your content type specific Javascript here. */

$(function() {
    function start_canvas() {

        // var content_width = jQuery('.container-fluid').width() * 0.5;
        // var stretch_x = content_width / 300;
        // jQuery('#tags-canvas').attr('width', content_width);
        // jQuery('#canvas-container').attr('width', content_width + 'px');
        // http://www.goat1000.com/tagcanvas.php
        if(!jQuery('#tags-canvas').tagcanvas({
            textColour : '#000',
            outlineColour: '#8BA6CF',
            outlineThickness: 3,
            outlineOffset: 3,
            maxSpeed : 0.05,
            freezeActive : false,
            //stretchX: stretch_x,
            decel: 0.99, // 0.95
            // tooltip: 'div',
            // tooltipClass: 'tags-tooltip',
            // tooltipDelay: 100,
            initial: [0.8, -0.3],
            noMouse: false,
            wheelZoom: false,
            imageScale: null,
            depth : 0.9
        }, 'tags')) {
            // TagCanvas failed to load
            $('#canvas-container').hide();
        }
    }
    start_canvas();
});
