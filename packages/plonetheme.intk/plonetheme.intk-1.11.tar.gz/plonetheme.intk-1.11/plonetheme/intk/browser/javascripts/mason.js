//TODO: keep an array of all images and wait for all of them to check in before running masonry

jq(window).load(function(){
    jq('.template-search .searchResults .tileItem').css({"opacity": "0"});
    jq('.template-search .searchResults').masonry({columnWidth:80, gutterWidth:40, itemSelector:'.tileItem', isResizable:true, animate:false});
    jq('.template-search .searchResults .tileItem').animate({"opacity": "1"}, 200);
});

jq(window).load(function(){
    jq('.template-intk_folder_view #content .tileItem').css({"opacity": "0"});
    jq('.template-intk_folder_view #masonContainer').masonry({columnWidth:80, gutterWidth:40, itemSelector:'.tileItem', isResizable:true, animate:false});
    jq('.template-intk_folder_view #masonContainer .tileItem').animate({"opacity": "1"}, 200);
});

$(window).resize(function() {
    resizer.run();   
});

resizer = {};
resizer.currentMode = "";
resizer.run = function(){
    var mode = ""
    if ($(window).width() >= 1328)
    { 
        mode = "xlarge";
    }
    else if ($(window).width() >= 1006)
    {
        mode = "large";
    }
    else if ($(window).width() >= 845)
    {
        mode = "medium";
    }
    else if ($(window).width() >= 0)
    {
        mode = "mobile";
    }
    
    if(mode != resizer.currentMode)
    {
        resizer.currentMode = mode
        $("body").removeClass("xlarge large medium small mobile");
        $("body").addClass(mode);
    }
};

resizer.refreshDebugDiv = function ()
{
    if ($("#debug").length == 1)
    {
        $("#debug").text($(window).width());
    }
    else
    {
        $("body").append('<div id="debug"></div>');
        $("#debug").css({'position':'fixed', 'right':'0', 'top':'0', 'background-color':'#000', 'color':'#fff', 'width':'50px', 'height':'20px', 'font-size':'11px'}).text($(window).width())
    }
}

//Taking care of the searchbox stuff
jq(function(){
    resizer.run();
    jq('#portal-searchbox').hover(
                function() {
                    if(!$('body').hasClass('mobile'))
                    {
                        var title = jq('#parent-fieldname-title').text();
                        if(title != "")
                        {
                            jq('#portal-searchbox #nolivesearchGadget').attr('value', jq.trim(title));
                        }
                        jq(this).stop().css({"opacity": "1"});
                    }
                    else
                    {
                        jq(this).css({"opacity": "1"});
                    }
                },
                function() {
                    if(!$('body').hasClass('mobile'))
                    {
                        if(jq('#portal-searchbox #nolivesearchGadget:focus').length == 0)
                        {
                            jq(this).stop().animate({"opacity": "0"}, 1000);
                        }
                    }
                    else
                    {
                        jq(this).css({"opacity": "1"});
                    }
                });
    
    jq('#portal-searchbox #nolivesearchGadget').focus(
            function(){
                if(!$('body').hasClass('mobile'))
                {
                    var title = jq('#parent-fieldname-title').text();
                    if(jq.trim(title) == jq('#portal-searchbox #nolivesearchGadget').attr('value'))
                    {
                        jq('#portal-searchbox #nolivesearchGadget').attr('value', "");
                    }
                }
                else
                {
                    jq(this).css({"opacity": "1"});
                }
            }).blur(function()
                {
                    if(!$('body').hasClass('mobile'))
                    {
                        var title = jq('#parent-fieldname-title').text();
                        if(title != "")
                        {
                            jq('#portal-searchbox #nolivesearchGadget').attr('value', jq.trim(title));
                        }
                        jq('#portal-searchbox').stop().animate({"opacity": "0"}, 1000);
                    }
                    else
                    {
                        jq(this).css({"opacity": "1"});
                    }
                }
            );
});