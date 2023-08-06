var ajaxManager = jq.manageAjax.create('queuedRequests', {
    queue: true,
    cacheResponse: false
});



simplelayout.toggleEditMode = function(enable, el){
    var $controls = jq('.sl-controls', jq(el));
    var $block = $controls.closest('.BlockOverallWrapper');

    if(enable){
        //show controls div
        $controls.show();
        if (!$block.hasClass("blockHighlight"))
            $block.addClass("blockHighlight");

        jq(".simplelayout-content").trigger('actionsloaded');

    }else{
        $block.removeClass("blockHighlight");
        $controls.hide();
    }

    var imgblocks = jq('.BlockOverallWrapper.image');
    for (var b=0;b<imgblocks.length;b++) {
        var query_controls = '#'+imgblocks[b].id + ' .sl-controls';
        var controls_el = jq(query_controls)[0];
        //simplelayout.setControlsWidth(controls_el);
    }
};

/* not really intuitive so far */
/*
simplelayout.expose = function(){
    var editable = jq('#portal-columns');
    var exposed =  editable.expose({api: true,
                                    opacity: 0.3,
                                    color:'black',
                                    zIndex:2000});

    return exposed;
}

*/

function gup( name, url )
{
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  if (typeof url == "undefined") {
      url = window.location.href;
      }
  var results = regex.exec( url );
  if( results === null )
    return "";
  else
    return results[1];
}

function getBaseUrl(){
    var bhref= base_href = jq('base')[0].href;
    if(bhref.substr(bhref.length-1,1)!='/'){
        bhref += "/";
        }
    return bhref;

}

simplelayout.refreshParagraph = function(item){
    //var item = this;
    var a_el = jq('a', item);
    var id = a_el[0].id.split("_");
    var uid = id[0];
    //outch we have to change this asap - it makes no sense
    var params = id[1].split('-');
    var layout = params[0];
    var cssclass = params[1];
    var viewname = params[2];
    if (cssclass==undefined){
        cssclass = '';
    }

    if (cssclass !== ''){
        layout = layout + '-' + cssclass;
    }

    if (viewname === undefined){
        viewname = '';
    }

    var fieldname = gup('fieldname',a_el[0].href);

    ajaxManager.add({url:'sl_ui_changelayout',
                            data:{ uid : uid, layout :layout,viewname:viewname,fieldname:fieldname },
                            success:function(data){
                                jq('#uid_' + uid +' .simplelayout-block-wrapper').replaceWith(data);
                                jq('#uid_' + uid +' .active').removeClass('active');
                                jq(item).addClass('active');
                                simplelayout.alignBlockToGridAction();
                                //simplelayout.setControlsWidth(item);
                                //trigger refreshed event
                                var $wrapper = jq(item).closest('.BlockOverallWrapper');
                                jq(".simplelayout-content:first").trigger('refreshed',[$wrapper]);
                                initializeSimplelayoutColorbox(jq('.sl-img-wrapper a'));
                                }
                            });
    return 0;

};

function activeSimpleLayoutControls(){
    jq(".sl-layout").bind("click", function(e){
            e.stopPropagation();
            e.preventDefault();

            simplelayout.refreshParagraph(this);

        });

}


function activateSimplelayoutActions(){
    // delete
    jq('.simplelayout-content a.sl-delete-action').each(function(i, o){
        var $this = jq(o);
        var uid = $this.closest('.BlockOverallWrapper').attr('id');
        $this.prepOverlay({
            subtype:'ajax',
            urlmatch:'$',urlreplace:' #content > *',
            formselector:'[action*=delete_confirmation]',
            noform:function(){
                //remove deleted block manually, because we won't reload the
                //hole page
                jq('#'+uid).hide('blind',function(){
                    jq(this).remove();
                });
                return 'close';
            },
            'closeselector':'[name=form.button.Cancel]'
        });
    });

}

jq(function(){
    jq(".simplelayout-content:first").bind("actionsloaded", activateSimplelayoutActions);
    jq(".simplelayout-content:first").bind("actionsloaded", activeSimpleLayoutControls);


    //bind mouseover/mouseout event on edit-button
    jq('div.simplelayout-content .BlockOverallWrapper').bind('mouseenter',function(e){
        e.stopPropagation();
        e.preventDefault();
        simplelayout.toggleEditMode(enable=true, el=this);
    });
    jq('div.simplelayout-content .BlockOverallWrapper').bind('mouseleave',function(e){
        e.stopPropagation();
        e.preventDefault();
        simplelayout.toggleEditMode(enable=false, el=this);
    });

    // Implement edit-bar slide
    jq('.sl-toggle-edit-bar-wrapper').bind('click', function(e){
        var $this = jq(this);
        var $bar = jq('.sl-toggle-edit-bar', $this);
        var $allbars = jq(this).closest('.simplelayout-content').find('.sl-toggle-edit-bar');
        var $wrapper = $this.closest('.simplelayout-content').find('.sl-actions-wrapper');
        if ($bar.hasClass('ui-icon-triangle-1-w')){
            $this.parent().css('width', '600px');
            $wrapper.addClass('showSimplelayoutControls');

            $allbars.removeClass('ui-icon-triangle-1-w').addClass('ui-icon-triangle-1-e');
        } else {
            $this.parent().css('width', '10px');
            $wrapper.removeClass('showSimplelayoutControls');
            $allbars.addClass('ui-icon-triangle-1-w');
        }
    });
});
