
//Activities Hack
$(function()
{
    if ($(".portlet.portletCollection").find(".portletItem").length == 0)
    {
        $(".portlet.portletCollection").hide();
    }
});

//Slideshow hack to go back from the info button
slideshowHack = {};
slideshowHack.referrer = document.referrer
slideshowHack.back = function (uuid)
{
    window.location = slideshowHack.referrer + "#" + uuid;
    return false;
};


//Show the next slide in the given slideshow
//OVERRIDE
mediaShow.next = function (slideshowIndex)
{
  var slideshow = mediaShow.slideshows[slideshowIndex];
  if(slideshow.currentSlide + 1 <= slideshow.size - 1)
  { 
    mediaShow.goToSlide(slideshow.currentSlide + 1, slideshow); 
  }
  else
  {
    mediaShow.nextObject(slideshow);
  }
  
  return false;
}

//Show the previews slide in given slideshow
//OVERRIDE
mediaShow.prev = function (slideshowIndex)
{
  var slideshow = mediaShow.slideshows[slideshowIndex];
  if(slideshow.currentSlide - 1 >= 0)
  {
    mediaShow.goToSlide(slideshow.currentSlide - 1, slideshow);
  }
  else
  {
    mediaShow.prevObject(slideshow);
  }
  
  return false;
}

mediaShow.nextObject = function (slideshow)
{
    //if ($('body').hasClass('portaltype-category-navigator'))
    //{
    //    window.location = 'next' + location.search;
    //}
    //else
    //{
        mediaShow.goToSlide(0, slideshow);
    //}
    
}

mediaShow.prevObject = function (slideshow)
{
    //if ($('body').hasClass('portaltype-category-navigator'))
    //{
    //    window.location = 'prev' + location.search;
    //}
    //else
    //{
        mediaShow.goToSlide(slideshow.size-1, slideshow);
    //}
}


//This starts loading a slide assynchrounosly and when it finishes loading it starts the next one
mediaShow.loadSlide = function (slideshow, slideNumber)
{
    var slide = slideshow.slides[slideNumber];
    var URL = slide.url + '/get_media_show_item';
    
    if(slideshow.presentation)
    {
      URL = slide.url + '/get_media_show_item?presentation=true'
    }
    else{
      URL = slide.url + '/get_media_show_item';
    }
    
    $.getJSON(URL, function(data, textStatus, jqXHR) {
        var slideContainer = $(slideshow.obj).find(".mediaShowSlide_" + slideNumber);
        
        if (slideNumber == 4)
        {
          test = "breakpoint";
        }
        
        //var titleDiv = '<div class="mediaShowTitle"><h2><a href="'+slide.url+'">'+data.title+'</a></h2></div>';
        var descriptionDiv = "";
        if(slideshow.presentation)
        {
          descriptionDiv = '<div class="mediaShowDescription">'+$("<div />").html(data.description).text();+'</div>';
        }
        else
        {
          descriptionDiv = $('<div class="mediaShowDescription">'+data.description+'</div>');
        }
        var infoDiv = $('<div class="mediaShowInfo"></div>');
        
        infoDiv.append(descriptionDiv);
        slideContainer.append(infoDiv);
        
        //INFO: Uncomment this if you want clickable pictures
        //var link = '<a class="media"></a><a class="infoButton" href="'+slide.url+'?came_from='+window.location.href+'" title="info">info</a>';
        var link = '<a class="media"></a><a class="infoButton" href="'+slide.url+'?clicked_on_info=true" title="info">info</a>';
        //var link = '<a class="media"></a><a class="infoButton" href="'+slide.url+'" title="info">info</a>';
        if (data.media.type == 'Video' || data.media.type == 'Youtube' || data.media.type == 'Vimeo')
        {
          var link = '<a class="media"></a>';
        }
        
        //INFO: Comment next line if you want clickable pictures 
        //var link = "<a></a>";
        
        slideContainer.append('<div class="mediaShowMedia mediaShowMediaType_'+data.media.type+'">'+link+'</div>');
        
        if (slideshow.height == 0)
        {
          slideshow.height = $(slideContainer).find(".mediaShowMedia").height();
          slideshow.width = $(slideContainer).find(".mediaShowMedia").width();
        }
        
        //TODO: Here I prepend the loader image but for now it is not working so well I need to change the loading event processing a bit no make it nicer.
        //slideContainer.find('.mediaShowMedia').prepend(mediaShow.loaderObj);
        
        slideContainer.find('.mediaShowMedia a.media').append(mediaShow.getMediaObject(data.media, slideshow));
        
        if(slideshow.presentation)
        {
          slideContainer.find('.mediaShowDescription').css({'top': '50%', 'margin-top': -(slideContainer.find('.mediaShowDescription').height()/2)});
        }
        
        slide.loaded = mediaShow.LOADED;
        
        //if( $('body.template-folder_slideshow_view').length > 0 )
        //{
        //    slideshow.obj.prepend($('<a name="'+slide.UID+'"></a>'));
        //}
        
        $(slideContainer).touchwipe({
            wipeLeft: function() {mediaShow.prev(mediaShow.indexOf(slideshow)) },
            wipeRight: function() { mediaShow.next(mediaShow.indexOf(slideshow)) },
            preventDefaultEvents: false
            });
        
        mediaShow.loadNext(slideshow);
    });
}

//This function adds the navigation buttons to the slideshow
mediaShow.addButtons = function (slideshow)
{ 
  var slideshowIndex = mediaShow.indexOf(slideshow);
  var buttonNext = $('<a href="#" class="buttonNext" onclick="return mediaShow.next('+slideshowIndex+')">&raquo;</a>').css('background-image', 'url('+mediaShow.buttonSprite+')');
  var buttonPrev = $('<a href="#" class="buttonPrev" onclick="return mediaShow.prev('+slideshowIndex+')">&laquo;</a>').css('background-image', 'url('+mediaShow.buttonSprite+')');
  var buttonFullscreen = $('<a href="#" class="buttonFullscreen" onclick="return mediaShow.fullscreen('+slideshowIndex+')">Fullscreen</a>');
  
  //var container = '<div class="mediaShowButtons">'+buttonPrev+buttonNext+'</div>';
  var container = $('<div class="mediaShowButtons"></div>');
  $(container).append(buttonPrev);
  $(container).append(buttonNext);
  slideshow.obj.append(container);
  slideshow.obj.append(buttonFullscreen);
}

//This switches on and off the fullscreen mode
mediaShow.fullscreen= function (slideshowIndex)
{
    var slideshow = mediaShow.slideshows[slideshowIndex];

    if (!$(slideshow.obj).hasClass("fullscreen"))
    {
       slideshow.oldParent = $(slideshow.obj).parent();
       slideshow.oldParentIndex = $(slideshow.obj).parent().children().index($(slideshow.obj))
       $('body').append(slideshow.obj);
       var arrowTooltip = $('<div id="ArrowToolTip">&nbsp;</div>');
       $('body').append(arrowTooltip);
       $(arrowTooltip).animate({'opacity':0},5000);
       
       $(slideshow.obj).addClass("fullscreen")
       $('body').addClass("fullscreen")
       if (!$.browser.msie)
       {
            mediaShow.reAlign()
       }
       $(slideshow.obj).focus();
       if ($(slideshow.obj)[0].mozRequestFullScreen) {
            // This is how to go into fullscren mode in Firefox
            // Note the "moz" prefix, which is short for Mozilla.
            $(slideshow.obj)[0].mozRequestFullScreen();
        } else if ($(slideshow.obj)[0].webkitRequestFullScreen) {
            // This is how to go into fullscreen mode in Chrome and Safari
            // Both of those browsers are based on the Webkit project, hence the same prefix.
            $(slideshow.obj)[0].webkitRequestFullScreen();
        }
    }
    else
    {
        if(slideshow.oldParent != undefined)
        {
            if (slideshow.oldParentIndex >= $(slideshow.oldParent).children().length )
            {
                $(slideshow.oldParent).append(slideshow.obj);
            }
            else
            {
                $(slideshow.obj).insertBefore($(slideshow.oldParent).children().get(slideshow.oldParentIndex))
            }
            
            slideshow.oldParent = undefined;
            slideshow.oldParentIndex = undefined;
        }
       $(slideshow.obj).removeClass("fullscreen")
       $('body').removeClass("fullscreen")
       $("#ArrowToolTip").remove()
        if (!$.browser.msie)
       {
            mediaShow.reAlign()
       }
    }
    
    return false;
}

mediaShow.reAlign = function ()
{   
    $.each(mediaShow.slideshows, function(index, slideshow)
         {
            // WIP refresh slideshow size
            var slideContainer = slideshow.obj.find(".mediaShowSlide_"+slideshow.currentSli);
            slideshow.height = $(slideContainer).find(".mediaShowMedia").height();
            slideshow.width = $(slideContainer).find(".mediaShowMedia").width();

            $.each(slideshow.slides, function(x, slide)
                   {
                      slideshow.obj.find(".mediaShowSlide_"+x).show();
                      slideshow.obj.find(".mediaShowSlide_"+x).find('.mediaShowDescription').css({'top': '50%', 'margin-top': -(slideshow.obj.find(".mediaShowSlide_"+x).find('.mediaShowDescription').height()/2)});
                      //var sizeOfContainer = slideshow.height
                      var sizeOfContainer = slideshow.obj.find(".mediaShowSlide_"+slideshow.currentSlide).find('.mediaShowMedia').height();
                      
                      var img = slideshow.obj.find(".mediaShowSlide_"+x).find('img')[0];
                      height = $(img).attr('offsetHeight');
                      if(height > 0 && height <= sizeOfContainer)
                      {
                        var margin = (sizeOfContainer - height)/2;
                        $(img).css('margin-top', margin);
                      }
                      slideshow.obj.find(".mediaShowSlide_"+x).hide();
                   });
            
            mediaShow.goToSlide(slideshow.currentSlide, slideshow);
          });
}

//Adding custom text to the buttons
$(function(){
    $('.buttonPrev').text("Vorige");
    $('.buttonNext').text("Volgende");
    $('.portlet-static-opening-2018eenmaal-andermaal .portletHeader span').wrap('<a href="http://www.porseleinplaats.nl/algemeen/eenmaal-andermaal-doc/eenmaal-andermaal-doc/"></a>');
});