/*
Annotation Plugin for flot.
http://github.com/vpelletier/flot-anotate
License: GPLv2+
 */

(function ($) {
    function init(plot) {
        plot.hooks.draw.push(function (plot, ctx) {
            
        });
    }
    $.plot.plugins.push({
        init: init,
        options: {
        },
        name: "annotate"
    });
})(jQuery);
