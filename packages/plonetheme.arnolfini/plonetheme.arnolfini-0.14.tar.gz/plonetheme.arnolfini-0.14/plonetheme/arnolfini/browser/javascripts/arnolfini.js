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

mediaShow.buttonPrevContent = "&larr;";
mediaShow.buttonNextContent = "&rarr;";

//Override slideshow behaviour
//Show the next slide in the given slideshow
mediaShow.next = function (slideshowIndex)
{
  var slideshow = mediaShow.slideshows[slideshowIndex];
  if(slideshow.currentSlide + 1 <= slideshow.size - 1)
  { 
    mediaShow.goToSlide(slideshow.currentSlide + 1, slideshow); 
  }
  else
  {
    Arnolfini.getNextEvent()
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
    Arnolfini.getPrevEvent()
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

Arnolfini.getNextEvent = function ()
{
	if (onSlodeshowSkipNext !== null)
	{
		window.location = onSlodeshowSkipNext;
	}
	
}

Arnolfini.getPrevEvent = function ()
{
	if (onSlodeshowSkipPrev!== null)
	{
		window.location = onSlodeshowSkipPrev + "#lastpic";
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
});

