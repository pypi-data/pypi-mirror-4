var jq = jQuery.noConflict();
jq(document).ready(function(){
    jq("div.big-target a").bigTarget({
        clickZone : 'div:eq(0)' // jQuery parent selector
    });
});
