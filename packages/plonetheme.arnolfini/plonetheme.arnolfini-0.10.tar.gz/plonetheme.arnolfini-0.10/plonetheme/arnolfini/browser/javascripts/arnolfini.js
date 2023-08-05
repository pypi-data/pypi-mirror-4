$.fn.hasOverflow = function() {
    var $this = $(this);
    var $children = $this.find('.tileMedia');
    var len = $children.length;

    if (len) {
        var maxWidth = 0;
        var maxHeight = 0
        $children.map(function(){
            maxWidth = Math.max(maxWidth, $(this).outerWidth(true));
            maxHeight = Math.max(maxHeight, $(this).outerHeight(true));
        });

        return maxWidth > $this.width() || maxHeight > $this.height();
    }

    return false;
};

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

$(document).ready(function() {
	Arnolfini.events();
	Arnolfini.archiveShowButtons();
});

