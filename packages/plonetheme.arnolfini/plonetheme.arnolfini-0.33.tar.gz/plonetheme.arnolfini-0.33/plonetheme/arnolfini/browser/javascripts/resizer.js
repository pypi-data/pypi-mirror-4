resizer = {};

resizer.currentMode = "";

resizer.run = function(){
    var mode = ""
    if ($(window).width() >= 1220)
    { 
        mode = "large";
    }
    else if ($(window).width() >= 1024)
    {
        mode = "medium";
    }
    else if ($(window).width() >= 768)
    {
        mode = "small";
    }
    else if ($(window).width() >= 0)
    {
        mode = "mobile";
    }
    
    if(mode != resizer.currentMode)
    {
        resizer.currentMode = mode
        $("body").removeClass("large medium small mobile");
        $("body").addClass(mode);
        //resizer.refreshDebugDiv();
        resizer.onResize();
    }
    
};

resizer.onResize = function ()
{
    
}

resizer.refreshDebugDiv = function ()
{
    if ($("#debug").length == 1)
    {
        //$("#debug").text($(window).width());
        $("#debug").text(resizer.currentMode);
    }
    else
    {
        $("body").append('<div id="debug"></div>');
        //$("#debug").css({'position':'fixed', 'right':'0', 'top':'0', 'background-color':'#000', 'color':'#fff', 'width':'50px', 'height':'20px', 'font-size':'11px'}).text($(window).width())
        $("#debug").css({'position':'fixed', 'right':'0', 'top':'0', 'background-color':'#000', 'color':'#fff', 'width':'50px', 'height':'20px', 'font-size':'11px'}).text(resizer.currentMode)
    }
}


$(window).load(function ()
{
    resizer.run();
    $(window).resize(function() {
        resizer.run();   
    });
});