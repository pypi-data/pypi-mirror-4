//Overriding glossary click

var glossary_popup_on = false;

function goto_glossary_definition(num)
{
    if (glossary_popup_on)
    {
        var node = $(this);
        popup_node = $("#glossary-definition-popup");
        if (popup_node.length > 0) {
            popup_node.hide();
        }
        glossary_popup_on = false;
    }
    else
    {
        var node = $(this);
        popup_node = $("#glossary-definition-popup");
        if (popup_node.length > 0) {
            popup_node.show();
        }
        glossary_popup_on = true;
    }
    
    return false;
}

PorseleinApp = {};

//Set a cookie
PorseleinApp.setCookie = function (name,value,days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
}

//Read a cookie value
PorseleinApp.getCookie = function (name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

//Delete a cookie
PorseleinApp.deleteCookie = function (name) {
    PorseleinApp.setCookie(name,"",-1);
}

//Fix links to keep in app mode
PorseleinApp.fixLinks = function()
{
    var a=document.getElementsByTagName("a");
    for(var i=0;i<a.length;i++) {
        if(!a[i].onclick && a[i].getAttribute("target") != "_blank") {
            a[i].onclick=function() {
                    window.location=this.getAttribute("href");
                    return false; 
            }
        }
    }
};

//Fix links to keep in app mode
PorseleinApp.fixLinks = function()
{
    var a=document.getElementsByTagName("a");
    for(var i=0;i<a.length;i++) {
        if(!a[i].onclick && a[i].getAttribute("target") != "_blank") {
            a[i].onclick=function() {
                    window.location=this.getAttribute("href");
                    return false; 
            }
        }
    }
};

PorseleinApp.getQueryVariable = function(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split('&');
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split('=');
        if (decodeURIComponent(pair[0]) == variable) {
            return decodeURIComponent(pair[1]);
        }
    }
    return null
}

//Stop bouncing
PorseleinApp.stopBounce = function ()
{
    $('body').attr('class')
    
    if(!$('body').hasClass('template_object'))
    {
        var xStart, yStart = 0;
        
        document.addEventListener('touchstart',function(e) {
            xStart = e.touches[0].screenX;
            yStart = e.touches[0].screenY;
        });
        
        document.addEventListener('touchmove',function(e) {
            var xMovement = Math.abs(e.touches[0].screenX - xStart);
            var yMovement = Math.abs(e.touches[0].screenY - yStart);
            //console.log("mov: " + xMovement + " / " + yMovement);
            if (xMovement <= yMovement*3)
            {
                e.preventDefault();
            }
        });
    } 
};

PorseleinApp.selfScroll = function ()
{
    var xStart, yStart = 0;
    var speed = 0;
    var innerWidth = $('.h_scroll').innerWidth();
    var dragged = false;

    document.addEventListener('touchstart',function(e) {
        xStart = e.touches[0].screenX;
        yStart = e.touches[0].screenY;
        $('.h_scroll').stop();
        innerWidth = $('.h_scroll').innerWidth();
        speed = 0;
        var dragged = false;
    });
    
    document.addEventListener('touchmove',function(e) {
        var dragged = true;
        
        var xMovement = e.touches[0].screenX - xStart;
        var yMovement = e.touches[0].screenY - yStart;
        
        xStart = e.touches[0].screenX;
        yStart = e.touches[0].screenY;
        if (xMovement < 5 && xMovement > -5)
        {
            speed = 0;
        }
        else
        {
            speed = xMovement * 5;
        }
        
    
        var xScroll = 0;
        var currentValue = $('.h_scroll').css("left");
        
        //console.log("XMovement: " + xMovement);
        if(typeof currentValue !== 'undefined')
        {
            xScroll = parseInt(currentValue.replace("px", "")) + xMovement;
        }
        else
        {
            xScroll = xMovement ;
        }
        
        
        //console.log("Screen width: " + screen.width);
        //console.log("xScroll: " + xScroll);
        //console.log("h_scroll width: " + ($('.h_scroll').innerWidth()));
        
        if(xScroll > -(innerWidth - screen.width) && xScroll <= 0 )
        {
            $('.h_scroll').css("left", xScroll);
        }
        
        e.preventDefault();
    });
    
    document.addEventListener('click',function(e) {
        if (dragged)
        {
            e.preventDefault();
        }
    });
    
    document.addEventListener('touchend',function(e) {
        
        if (speed == 0)
        {
            return true;
        }
        var currentValue = parseInt($('.h_scroll').css("left").replace("px", ""));
        var finalValue = currentValue + speed;
        
        console.log("Animating!");
        console.log("Speed = " + speed);
        console.log("currentValue = " + currentValue);
        console.log("finalValue = " + finalValue);
        
        if (finalValue >= 0)
        {
            finalValue = 0;
        }
        else if (finalValue < -(innerWidth - screen.width))
        {
            finalValue = -(innerWidth - screen.width)
        }
        
        $('.h_scroll').animate({"left": finalValue}, Math.abs(speed)+500, "easeOutCirc");
        
        e.preventDefault();
        return false;
    });
};

PorseleinApp.loaded = function()
{
    $('.content_wrapper').show();
    $('#spinner').hide();
}

PorseleinApp.loader = function ()
{
    $(window).load(PorseleinApp.loaded);
}

PorseleinApp.closeLightbox = function ()
{
    mediaShow.stopAllVideos();
    $(".lightbox").hide();
}

PorseleinApp.openLightbox = function ()
{
    var videolead = $('.videolead');
    if (videolead.length > 0)
    {
        var classes = $(videolead[0]).attr('class');
        var uid = classes.substring(classes.indexOf('uid_')+4);
        var slideshow = mediaShow.slideshows[0];
        var i = mediaShow.idToIndex(slideshow, uid);
        mediaShow.goToSlide(i, slideshow);
    }
    $(".lightbox").show();
}

PorseleinApp.addToHomeTip = function()
{
    var isRanFromHomeScreen = navigator.standalone;
    var isiPad = navigator.userAgent.match(/iPad/i) != null; 
    var closedTipBoxValue = PorseleinApp.getCookie('closedTipBox');
    var closedTipBox = false;
    
    if (closedTipBoxValue === "true")
    {
        closedTipBox = true;
    }

    
    if (!closedTipBox && isiPad && !isRanFromHomeScreen)
    {
        //alert("You should run this in full screen");
        var img = $('<img class="tipBoxImage" src="++resource++plonetheme.porseleinplaats.images/addToHome.png">');
        var text = $('<p class="tipBoxText">Om de \'Eenmaal, andermaal\' Web App direct vanaf uw startscherm te gebruiken,  klik op de knop hierboven en kies voor <strong>\'Zet in beginscherm\'</strong>.</p>');
        var arrow = $('<div class="tipBoxArrow"></div>');
        var closeButton = $('<div class="tipBoxClose" onclick="PorseleinApp.closeTipBoxForever();"></div>');
        var box = $('<div class="tipBox"></div>');
        
        box.append(arrow);
        box.append(closeButton);
        box.append(img);
        box.append(text);
        box.css('opacity', 0);
        $('body').append(box);
        box.animate({'opacity': 1}, 600);
        setTimeout(PorseleinApp.closeTipBox, 10000);
    }
}

PorseleinApp.closeTipBox = function ()
{
    $('.tipBox').animate({'opacity': 0}, 600, function () {$('.tipBox').remove();});
}

PorseleinApp.closeTipBoxForever = function ()
{
    $('.tipBox').remove();
    PorseleinApp.setCookie('closedTipBox', true, 30)
}

PorseleinApp.fixHeight = function ()
{
    var height = $(window).height()-130;
    var padding = (height/2)-300;
    if (padding > 0)
    {
        $(".scroll").css('padding-top', padding + "px");
        $(".scroll").css('height', height - padding + "px"); 
    }
    else
    {
        $(".scroll").css('height', height + "px");
        $(".scroll").css('padding-top', "0px");
    }
    
    if ($("body.template_home").length == 1)
    {   
        var height = $(window).height()-130;
        var padding = (height/2)-300;
        
        if (padding > 0)
        {
            $(".content_wrapper").css('padding-top', padding + "px");
            $(".content_wrapper").css('height', height - padding + "px");
        }
        else
        {
            $(".content_wrapper").css('height', height + "px");
            $(".content_wrapper").css('padding-top',  "0px");
        }
    }
};

$(function(){
    PorseleinApp.loader();
    PorseleinApp.fixLinks();
    PorseleinApp.fixHeight();
    $(window).resize(PorseleinApp.fixHeight);
    //PorseleinApp.stopBounce();
    //PorseleinApp.selfScroll();
    //PorseleinApp.iscroll();
});

























/*
// Temporary stuff
//=================================

//Definition of a page
function Page ()
{
    this.obj = $('<div class="page"></div>');
    this.loaded = false;
    this.URL = null;
}

Page.prototype.load = function ()
{
    if (this.URL !== null)
    {
        
    }
}
//================


//Stores the current pages, basically keeps the content
PorseleinApp.pages = [];

//Checks for existing pages on the current content and syncs the arry to that
PorseleinApp.sync = function ()
{
    
}

//Checks if the page exists
PorseleinApp.find = function()
{
    for (page in this.pages)
    {
        
    }
}

//Ads a page to the end of the stack, returns the position of the new page
PorseleinApp.addPage = function(page)
{
    PorseleinApp.pages.push(page);
    return PorseleinApp.pages.length -1;
};

//Removes a page from the stack
PorseleinApp.removePage = function (position)
{
    
};

//Move a page to a new position
PorseleinApp.movePage = function(origin, destination)
{
    
};

//Initialize everything and prepare for operation
PorseleinApp.init = function()
{
    
};

//Touchstart event
PorseleinApp.touchstart = function (e)
{
    
};

//Touchmove event
PorseleinApp.touchmove = function(e)
{
    
};

//Register the events
PorseleinApp.registerEvents = function(e)
{
    
};

//=================================
*/