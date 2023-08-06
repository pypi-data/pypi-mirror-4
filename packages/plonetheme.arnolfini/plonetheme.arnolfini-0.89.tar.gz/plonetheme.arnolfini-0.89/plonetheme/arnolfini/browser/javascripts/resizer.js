//Fix Chrome ans safari confusion in jquery
var userAgent = navigator.userAgent.toLowerCase(); 
$.browser.chrome = /chrome/.test(userAgent);
$.browser.windows = /windows/.test(userAgent);

// Is this a version of Chrome?
if($.browser.chrome){
  userAgent = userAgent.substring(userAgent.indexOf('chrome/') +7);
  userAgent = userAgent.substring(0,userAgent.indexOf('.'));
  $.browser.version = userAgent;
  // If it is chrome then jQuery thinks it's safari so we have to tell it it isn't
  $.browser.safari = false;
}

// Is this a version of Safari?
if($.browser.safari){
  userAgent = userAgent.substring(userAgent.indexOf('version/') +8);
  userAgent = userAgent.substring(0,userAgent.indexOf('.'));
  $.browser.version = userAgent;
}

resizer = {};

resizer.currentMode = "";

resizer.debug = false;

resizer.getWidth = function ()
{
    var browserWidth = window.innerWidth || document.documentElement.clientWidth;
    var jqueryWidth = $(window).width()
    var width = Math.max(jqueryWidth, browserWidth);
    if ($.browser.safari)
    {
        return width - 15;
    }
    else if ($.browser.chrome)
    {
        if ($.browser.windows)
        {
            return width - 17;
        }
        else
        {
            return width - 15;
        }
        
    }
    else if($.browser.msie)
    {
        return width;
    }
    else
    {
        return width;
    }
}

resizer.run = function(){
    var width = resizer.getWidth();
    
    var mode = ""
    if (width >= 1220)
    { 
        mode = "large";
    }
    else if (width >= 1006)
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
    
    if (resizer.debug === true)
    {
        resizer.refreshDebugDiv();
    }
    
};

resizer.onResize = function ()
{
    
}

resizer.refreshDebugDiv = function ()
{
    var width = resizer.getWidth();
    if (resizer.debug === true)  
    {
        if ($("#debug").length == 1)
        {
            $("#debug").text(width);
            //$("#debug").text(resizer.currentMode);
            //$("#debug").text($.browser.webkit);
        }
        else
        {
            $("body").append('<div id="debug"></div>');
            $("#debug").css({'position':'fixed', 'right':'0', 'top':'0', 'background-color':'#000', 'color':'#fff', 'width':'50px', 'height':'20px', 'font-size':'11px'}).text(width)
            //$("#debug").css({'position':'fixed', 'right':'0', 'top':'0', 'background-color':'#000', 'color':'#fff', 'width':'50px', 'height':'20px', 'font-size':'11px'}).text(resizer.currentMode)
        }
    }
}


$(window).load(function ()
{
    resizer.run();
    $(window).resize(function() {
        resizer.run();   
    });
});