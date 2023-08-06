jQuery(function($){

    // Detect floated images on the very right side and remove padding-right/
    // margin-right (so it will fit to the right border)


    simplelayout.arangeImages = function(){
        var $images = $('.BlockOverallWrapper.image.leftFloatable .sl-img-wrapper');

        // reset
        $images.removeClass('SLNoPaddingRight').removeClass('SLPaddingRight');
        //$images.each(function(i, o){
        for (var i = 0; i < $images.length; i++){
            var o  = $images[i];

            // store previous image offset
            if (i > 0){
                var $prev = $current;
            }else{
                var $current = $(o);
                continue;
            }
            $current = $(o);
            var current_offsety = $current.offset().top;
            var prev_offsety = $prev.offset().top;

            if (prev_offsety < current_offsety){
                $prev.addClass('SLNoPaddingRight');

            }else{
                $prev.addClass('SLPaddingRight');
            }
        }
    };


     simplelayout.arangeImages();
     //also bind event to block refreshed event
      $(".simplelayout-content:first").bind('refreshed', simplelayout.arangeImages);
});
