function hideCookiePolicy() {
    jQuery("#viewlet-cookiepolicy").each(function() {
        jQuery(this).slideUp(500);
    });
}
function displayCookiePolicy() {
    jQuery("#viewlet-cookiepolicy").each(function() {
        jQuery(this).slideDown(500);
    });
}
jQuery(function() {
    var btn = document.getElementById("tlspu_cookiepolicy_button")
    var chk = document.getElementById("tlspu_cookiepolicy_agreed")

    if (btn == null) {
        return;
    }

    btn.onclick = function() {
        acceptCookiePolicy();
        return false;
    };
    chk.onclick = function() {
        if (chk.checked) {
            btn.disabled = false;
        } else {
            btn.disabled = true;
        }
    };
    function acceptCookiePolicy() {
        var date = new Date();
        date.setTime(date.getTime()+(90*24*60*60*1000));
        var expires = "; expires="+date.toGMTString();
        document.cookie = "cookie-policy=accepted"+expires+"; path=/";
        hideCookiePolicy();
        return false;
    }
    function confirmAcceptCookiePolicy()
    {   
        if (document.getElementById("cookie-agreed").checked) {
            acceptCookiePolicy();
        } else {
            // This should never happen unless users are removing the disabled flag themselves.
            alert("You must confirm that you have read and understood this message before dismissing it."); 
        }
    }
    
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1,c.length);
        }
        if (c.indexOf("cookie-policy=") == 0) {
            acceptCookiePolicy();
            return;
        }
    }
    setTimeout(displayCookiePolicy, 1000);
});
