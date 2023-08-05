var edmlisting = {};
edmlisting.initoverlay = function(){
    jQuery('.edm-edit-popup').unbind('mouseover').mouseover(function(){
        jQuery(this).prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: '.edit-popup form',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
        	redirect: $.plonepopups.redirectbasehref
            });
        jQuery(this).removeClass('edm-edit-popup');
    });
    jQuery('.edm-delete-popup').unbind('mouseover').mouseover(function(){
        jQuery(this).prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            closeselector: '[name=form.button.Cancel]',
            formselector: '#edit-popup-transitions form',
            noform: function(el) {return $.plonepopups.noformerrorshow(el, 'redirect');},
        	redirect: $.plonepopups.redirectbasehref
            });
        jQuery(this).removeClass('edm-delete-popup');
    });
    jQuery('.edm-author-popup').unbind('mouseover').mouseover(function(){
        jQuery(this).prepOverlay({
            subtype: 'ajax',
            filter: common_content_filter,
            formselector: 'form'
            });
        jQuery(this).removeClass('edm-author-popup');
    });
    jQuery('.edm-quickview-popup').unbind('mouseover').mouseover(function(){
        jQuery(this).prepOverlay({
            subtype: 'image',
            filter: common_content_filter,
            });
        jQuery(this).removeClass('edm-quickview-popup');
    });

    // Content history popup
    jQuery('.edm-history-popup').prepOverlay({
       subtype: 'ajax',
       filter: 'h2, #content-history',
       urlmatch: '@@historyview',
       urlreplace: '@@contenthistorypopup'
    });

};
jQuery(document).ready(edmlisting.initoverlay);
