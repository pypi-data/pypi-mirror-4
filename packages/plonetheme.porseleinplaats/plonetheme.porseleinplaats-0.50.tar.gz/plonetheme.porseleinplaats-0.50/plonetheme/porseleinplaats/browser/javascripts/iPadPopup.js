// Detection of iPads and creating a popup to anounce a ipad webApp

iPadPopup = {};

iPadPopup.isiPad = navigator.userAgent.match(/iPad/i) != null;

iPadPopup.isHomePage = window.location['pathname'] === "/" || window.location['pathname'] === "/porseleinplaats/" || window.location['pathname'] === "/porseleinplaats" ;

iPadPopup.run = function ()
{
    var ClosedForeverValue = iPadPopup.getCookie("isiPadPopUpClosedForever");
    var isClosedForever = false;
    
    if (ClosedForeverValue === "true")
    {
        isClosedForever = true;
    }
    
    if (iPadPopup.isiPad && !isClosedForever && iPadPopup.isHomePage)
    {
        iPadPopup.open();
    }
};

iPadPopup.open = function ()
{
    //TODO: design;
        var title = $("<h1>Zeuws Museum App</h1>");
        var img = $('<img src="++resource++plonetheme.porseleinplaats.images/IconPorseleinPopUp.png" width="250" height="250" />')
        var text = $('<p class="tipBoxText">Voor de beste ervaring van Eenmaal, Andermaal op uw iPad, adviseren wij u om over te schakelen naar de nieuwe Zeeuws Museum app. Als u de link volgt, opent deze automatisch. <a class="iPadPopUpButton" href="http://app.porseleinplaats.nl">Schakel nu over naar app.porseleinplaats.nl</a></p>');
        var closeButton = $('<div class="iPadPopUpClose" onclick="iPadPopup.close();"></div>');
        var closeForever = $('<div class="closeForeverMsg"><input id="closeForever" type="checkbox" /> Toon dit bericht niet opnieuw. </div>')
        var box = $('<div class="iPadPopUp"></div>');
        var popup_body = $('<div class="iPadPopUpBody"></div>');
        
        popup_body.append(closeButton);
        popup_body.append(img);
        popup_body.append(title);
        popup_body.append(text);
        popup_body.append(closeForever);
        box.append(popup_body);
        $('body').append(box);
        $('body').css({'position': 'fixed',  'width':'100%', 'height':'100%' ,'overflow-y':'hidden'});
        
        $('.iPadPopUpButton').bind('touchstart', function (){$('.iPadPopUpButton').addClass('active')});
        $('.iPadPopUpButton').bind('touchend', function (){$('.iPadPopUpButton').removeClass('active')});
};

iPadPopup.close = function ()
{
    if($('#closeForever').attr('checked'))
    {
        iPadPopup.closeForever();
    }
    
    $('body .iPadPopUp').remove();
    $('body').css({'position': 'static',  'width':'auto', 'height':'auto' ,'overflow-y':'auto'});
};

iPadPopup.closeForever = function ()
{
    iPadPopup.setCookie("isiPadPopUpClosedForever", "true", 365);
};

//Set a cookie
iPadPopup.setCookie = function (name,value,days)
{
    if (days) {
        var date = new Date();
        date.setTime(date.getTime()+(days*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
    }
    else var expires = "";
    document.cookie = name+"="+value+expires+"; path=/";
};

//Read a cookie value
iPadPopup.getCookie = function (name)
{
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
};

//Delete a cookie
iPadPopup.deleteCookie = function (name)
{
    iPadPopup.setCookie(name,"",-1);
};

$(function ()
{
    iPadPopup.run();
});