Arnolfini = {};

Arnolfini.bodyclick = false
Arnolfini.searchopen = false
Arnolfini.menuopen = false

Arnolfini.doesBlockOverflow = function (block)
{
	var $this = $(block);
	var $children = $this.find('.tileMedia');
	var len = $children.length;
	
	return len > 3;
}

Arnolfini.archiveShowButtons = function ()
{
	$('.archiveBlocks').each(function ()
				 {
					if (Arnolfini.doesBlockOverflow($(this)))
					{
						$(this).find('.archiveViewAllButton').show();
					}
				})
}

Arnolfini.events = function ()
{
	// show search form on click
	$('.showmenu a').click(function(event) {
		if (!Arnolfini.menuopen) {
			$('#portal-globalnav').fadeIn();
			$('#portal-globalnav').addClass('openelement');
			Arnolfini.bodyclick = true
			Arnolfini.menuopen = true
		}
		else
		{
			//Close the menu on second click
			$('.openelement').fadeOut('fast');
			$('.openelement').removeClass('openelement');
			Arnolfini.searchopen = false;
			Arnolfini.menuopen = false;
			Arnolfini.bodyclick = false;
		}
		event.stopPropagation();
		return false;
	});
	
	// show search form on click
	$('.headerSearch .searchButton').click(function(event) {
		event.stopPropagation();
		if (Arnolfini.searchopen) {
			$('#nolivesearchGadget_form').submit();
		} else {
			$('.searchField').fadeIn();
			$('.searchField').addClass('openelement');
			$('.searchField').focus();
			Arnolfini.bodyclick = true
			Arnolfini.searchopen = true
		}
		return false;
	});
	
	// when the menu or the search box are open, we close them on body click
	$("body").click(function(event) {	
		if (Arnolfini.bodyclick && !$(event.target).is('.openelement, a') && !$(event.target).closest('.openelement').length) {
			event.stopPropagation();
			$('.openelement').fadeOut('fast');
			$('.openelement').removeClass('openelement');
			Arnolfini.searchopen = false;
			Arnolfini.menuopen = false;
			Arnolfini.bodyclick = false;
		}
	});
	
	//For iphone and ipad
	if (navigator.appName != "Microsoft Internet Explorer")
	{
		document.addEventListener('touchend',function(event) {
			if (Arnolfini.bodyclick && !$(event.target).is('.openelement, a') && !$(event.target).closest('.openelement').length) {
				event.stopPropagation();
				$('.openelement').fadeOut('fast');
				$('.openelement').removeClass('openelement');
				Arnolfini.searchopen = false;
				Arnolfini.menuopen = false;
				Arnolfini.bodyclick = false;
			}
		});
	}

}

mediaShow.buttonPrevContent = "&larr;";
mediaShow.buttonNextContent = "&rarr;";

//Override slideshow behaviour
//Show the next slide in the given slideshow
onSlodeshowSkipNext = null;
onSlodeshowSkipPrev = null;

mediaShow.next = function (slideshowIndex)
{
  var slideshow = mediaShow.slideshows[slideshowIndex];
  if(slideshow.currentSlide + 1 <= slideshow.size - 1)
  { 
    mediaShow.goToSlide(slideshow.currentSlide + 1, slideshow); 
  }
  else
  {
    Arnolfini.getNextEvent(slideshow)
  }
  
  return false;
}

//Show the previews slide in given slideshow
mediaShow.prev = function (slideshowIndex)
{
  var slideshow = mediaShow.slideshows[slideshowIndex];
  if(slideshow.currentSlide - 1 >= 0)
  {
    mediaShow.goToSlide(slideshow.currentSlide - 1, slideshow);
  }
  else
  {
    Arnolfini.getPrevEvent(slideshow)
  }
  
  return false;
}

//This reads the URL hash and updates the slideshows acordingly
mediaShow.readURLAndUpdate = function ()
{
  var hash = document.location.hash;
  if(hash == "")
    return;
  
  if(hash == "#lastpic")
  {
	document.location.hash = "";
	$.each(mediaShow.slideshows, function(index, slideshow)
	       {
			mediaShow.updateURL(slideshow, slideshow.slides.length -1);
	       });
  }
  
  var hash_split = hash.substring(1,hash.length).split(",");
  $.each(hash_split, function(index, hsh){
    $.each(mediaShow.slideshows, function(index, slideshow){
      var slideIndex = mediaShow.idToIndex(slideshow, hsh);
      if (slideIndex > -1)
      {
        slideshow.hash = hsh;
        mediaShow.goToSlide(slideIndex, slideshow);
        return false;
      }
      return true;
    });
  });
};

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
        /*var link = '<a href="'+slide.url+'"></a>';
        if (data.media.type == 'Video' || data.media.type == 'Youtube' || data.media.type == 'Vimeo')
        {
          var link = "<a></a>";
        }*/
        
        //INFO: Comment next line if you want clickable pictures 
        var link = '<a onclick="mediaShow.next('+mediaShow.indexOf(slideshow)+');"></a>';
        
        slideContainer.append('<div class="mediaShowMedia mediaShowMediaType_'+data.media.type+'">'+link+'</div>');
        
        if (slideshow.height == 0)
        {
          slideshow.height = $(slideContainer).find(".mediaShowMedia").height();
          slideshow.width = $(slideContainer).find(".mediaShowMedia").width();
        }
        
        //TODO: Here I prepend the loader image but for now it is not working so well I need to change the loading event processing a bit no make it nicer.
        //slideContainer.find('.mediaShowMedia').prepend(mediaShow.loaderObj);
        
        slideContainer.find('.mediaShowMedia a').append(mediaShow.getMediaObject(data.media, slideshow));
        
        if(slideshow.presentation)
        {
          slideContainer.find('.mediaShowDescription').css({'top': '50%', 'margin-top': -(slideContainer.find('.mediaShowDescription').height()/2)});
        }
        
        slide.loaded = mediaShow.LOADED;
        
        $(slideContainer).touchwipe({
            wipeLeft: function() {mediaShow.prev(mediaShow.indexOf(slideshow)) },
            wipeRight: function() { mediaShow.next(mediaShow.indexOf(slideshow)) },
            preventDefaultEvents: false
        });
        
        mediaShow.loadNext(slideshow);
    });
}

Arnolfini.getNextEvent = function (slideshow)
{
	if (onSlodeshowSkipNext !== null)
	{
		window.location = onSlodeshowSkipNext;
	}
	else
	{
		mediaShow.goToSlide(0, slideshow);
	}
}

Arnolfini.getPrevEvent = function (slideshow)
{
	if (onSlodeshowSkipPrev !== null)
	{
		window.location = onSlodeshowSkipPrev + "#lastpic";
	}
	else
	{
		mediaShow.goToSlide(slideshow.size-1, slideshow);
	}
}

mediaShow.getContentListing = function (slideshow)
{
    var URL, querystring;
    //extract passed query string
    if (slideshow.url.indexOf("?") != -1)
    {
        //there is a query string
        querystring = slideshow.url.slice(slideshow.url.indexOf("?") +1)
        slideshow.url = slideshow.url.slice(0, slideshow.url.indexOf("?"))
    }
    else
    {
        //There is no query string
        querystring = ""
    }
    
    if (slideshow.recursive)
    {
        if (querystring == "")
        {
            URL = slideshow.url + '/mediaShowListing';
        }
        else
        {
            URL = slideshow.url + '/mediaShowListing' + '?' + querystring;
        }
    }
    else
    {
        if (querystring == "")
        {
            URL = slideshow.url + '/mediaShowListing?recursive=false'
        }
        else
        {
            URL = slideshow.url + '/mediaShowListing' + '?' + querystring + "&recursive=false";
        }
    }
    
    $.getJSON(URL, function(data) {

        $.each(data, function(index, item) {
            //-------------------- Declaration of Slide ------------------
            slideshow.slides.push({
                "url":item.url,
                "UID" : item.UID,
                "loaded": mediaShow.NOT_LOADED
                });
            slideshow.size++;
        });
        
        if (slideshow.slides.length == 0)
        {
            $.each(mediaShow.slideshows, function(index, item){
                if(slideshow == item)
                {
                    mediaShow.slideshows.splice(index,1);
                    slideshow.obj.remove();
                }
            });
        }
        else
        {
            //If there is only one slide disable the buttons
            if (slideshow.slides.length == 1)
            {
		if (onSlodeshowSkipPrev == null)
		{
			$(slideshow.obj).find(".mediaShowButtons").addClass("disabled")
		}
            }
            mediaShow.markAsInitialized(slideshow);
        }
    });
}

Arnolfini.portletLinks = function ()
{
	$('.portletStaticText ul li a').not("#FooterPortletManager .portletStaticText ul li a").each(function()
		{
			var elem = $(this);
			var URL = $(this).attr("href") + '/get_number_of_results';
			
			$.getJSON(URL, function(data)
				  {
					if (data != null)
					{
						var count = $('<span class="resultCount"> '+data+'</span>')
						elem.after(count);
						if (data == 0)
						{
							elem.hide();
						}
					}
				  });
		});
};

/*   resizer handler */
resizer.onResize = function ()
{
	if (resizer.currentMode == "small" || resizer.currentMode == "mobile")
	{
		$('#portal-column-one').masonry({columnWidth:189, gutterWidth:69, itemSelector:'.portletWrapper', isResizable:true, animate:false});
		$('#portal-column-two').masonry({columnWidth:189, gutterWidth:69, itemSelector:'.portletWrapper', isResizable:true, animate:false});
		
	}
	else
	{
		$('#portal-column-one').masonry( 'destroy' );
		$('#portal-column-two').masonry( 'destroy' );
	}
}

$(document).ready(function() {
	Arnolfini.events();
	Arnolfini.archiveShowButtons();
	if ($(".columns").length > 0)
	{
		 var currentLetter= "";
		 $('.separateByLetters').find('h2.summary a').each(function ()
				{
					var name = $(this).text();
					firstLetter = name[0].toUpperCase();
					if (firstLetter != currentLetter)
					{
						currentLetter = firstLetter;
						$(this).parent().prepend($('<a class="letter dontend" name="'+firstLetter+'">'+firstLetter+'</a>'));
					}
				});
		 $('.columns').columnize({ width:300 });
	}
	
	Arnolfini.portletLinks();
});

