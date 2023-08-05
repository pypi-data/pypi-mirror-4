var SEMINAR = {}

SEMINAR.loadSpeakerDetails = function () {
    jQuery.ajax({
        type: 'GET',
        url: this.href,
        beforeSend: function() {
           setTimeout("jQuery.fancybox.showActivity()", 1)
        },
        success: function(data) {
            jQuery("#speaker-overlay #content")
                .replaceWith(jQuery(data)
                             .find("#content"));
        },
        complete: jQuery.fancybox.hideActivity,
    });
};

jQuery(document).ready(function() {
    if (jQuery("a.speaker-fancybox").length>0) {
        jQuery("a.speaker-fancybox").fancybox({
            'transitionIn'   : 'elastic',
            'transitionOut'  : 'elastic',
            'titlePosition'  : 'over',
            'overlayOpacity' : 0.7,
            'overlayColor'   : '#000',
            'showNavArrows'  : false,
            'onStart'        : SEMINAR.loadSpeakerDetails,
            'content'        : jQuery('#speaker-overlay'),
        });
    }
})
