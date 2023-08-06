$(function() {
    $(".simplelayout-content:first").bind('refreshed',function(e, $el){
        initFlowplayer($el);
    });
});