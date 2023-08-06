jQuery(function($) {
    $('.portletGoogleCalendar a').prepOverlay({
        subtype: 'ajax',
        cssclass: 'overlay-calendarevent',
        filter: common_content_filter
    });
});
