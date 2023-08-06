// toggle fullscreenmode with buttons
jq(document).ready(function() {

    // get current values for restoring after leaving fullscreen
    var columnwidth = jq('#portal-column-content').width();
    var columnmarge = jq('#portal-column-content').css('margin-left');
    
    // get more values from plone's css for fullscreenmode
    var fullwidth = jq('.width-full').width();
    var leftmarge = jq('.position-0').css('margin-left');
    

    // enter fullscreen
    jq('#togglesitefullscreen-on').click(function fullScreen() {
        
        // hide top- and footer-elements
        jq('#portal-top').hide();
        jq('#portal-breadcrumbs').hide();
        jq('#edit-bar').hide();
        jq('#portal-footer').hide();
        jq('#portal-colophon').hide();
        jq('#portal-siteactions').hide();
        
        // hide left- and right-column
        jq('#portal-column-one').hide();
        jq('#portal-column-two').hide();
        
        // set new values for contentarea
        jq('#portal-column-content').width(fullwidth);
        jq('#portal-column-content').css('margin-left',leftmarge);
        
        // switch button's apperance
        jq('#togglesitefullscreen-off').show();
        jq('#togglesitefullscreen-on').hide();
    });
    

    // leave fullscreen 
        jq('#togglesitefullscreen-off').click(function leaveFullScreen() {

        // show top- and footer-elements
        jq('#portal-top').show();
        jq('#portal-breadcrumbs').show();
        jq('#edit-bar').show();
        jq('#portal-footer').show();
        jq('#portal-colophon').show();
        jq('#portal-siteactions').show();
        
        // show left- and right-column
        jq('#portal-column-one').show();
        jq('#portal-column-two').show();

        // restore former values
        jq('#portal-column-content').width(columnwidth);
        jq('#portal-column-content').css('margin-left',columnmarge);

        // switch button's apperance back
        jq('#togglesitefullscreen-on').show();
        jq('#togglesitefullscreen-off').hide();
    });

});

