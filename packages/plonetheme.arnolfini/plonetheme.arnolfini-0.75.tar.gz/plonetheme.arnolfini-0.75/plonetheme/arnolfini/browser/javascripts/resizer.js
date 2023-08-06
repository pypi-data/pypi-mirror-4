resizer = {};

resizer.currentMode = "";

resizer.run = function(){
    var browserWidth = window.innerWidth || document.documentElement.clientWidth;
    var jqueryWidth = $(window).width()
    var width = Math.max(jqueryWidth, browserWidth);
    
    var mode = ""
    if (width >= 1220)
    { 
        mode = "large";
    }
    else if (($.browser.webkit && width >= 1039) || (!$.browser.webkit && width >= 1024))
    {
        mode = "medium";
    }
    else if (width >= 768)
    {
        mode = "small";
    }
    else if (width >= 0)
    {
        mode = "mobile";
    }
    
    if(mode != resizer.currentMode)
    {
        resizer.currentMode = mode
        $("body").removeClass("large medium small mobile");
        $("body").addClass(mode);
        resizer.onResize();
    }
    //resizer.refreshDebugDiv();
};

resizer.onResize = function ()
{
    
}

resizer.refreshDebugDiv = function ()
{
    var browserWidth = window.innerWidth || document.documentElement.clientWidth;
    var jqueryWidth = $(window).width()
    var width = Math.max(jqueryWidth, browserWidth);   
    if ($("#debug").length == 1)
    {
        $("#debug").text(width);
        //$("#debug").text(resizer.currentMode);
        //$("#debug").text($.browser.webkit);
    }
    else
    {
        $("body").append('<div id="debug"></div>');
        //$("#debug").css({'position':'fixed', 'right':'0', 'top':'0', 'background-color':'#000', 'color':'#fff', 'width':'50px', 'height':'20px', 'font-size':'11px'}).text(width)
        //$("#debug").css({'position':'fixed', 'right':'0', 'top':'0', 'background-color':'#000', 'color':'#fff', 'width':'50px', 'height':'20px', 'font-size':'11px'}).text(resizer.currentMode)
    }
}


$(window).load(function ()
{
    resizer.run();
    $(window).resize(function() {
        resizer.run();   
    });
});