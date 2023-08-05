var jquitr = {}
// modified output of http://jqueryui.com/themeroller/developertool/developertool.js.php
// this is used to make edit of existing themes work (note the hash for the iframe src)
var wrapper = function(hash) {
    jquitr.trString = '';
    var addThemeRoller = function(){
	if(jq('#inline_themeroller').size() > 0){
	    jq('#inline_themeroller').fadeIn();
	}
	else {
	    jq('<div id="inline_themeroller" style="display: none; position: fixed; background: #111; top: 25px; right: 25px; padding: 22px 0 15px 4px;width: 245px;height:400px; -webkit-border-radius: 6px; -moz-border-radius: 6px; z-index: 9999999;">'+
	      '<a href="#" class="closeTR" style="font-family: Verdana, sans-serif; font-size: 10px; display: block; position: absolute; right: 0; top: 2px; text-align: right; background: url(http://jqueryui.com/themeroller/developertool/icon_bookmarklet_close.gif) 0 2px no-repeat; width: 16px;height: 16px; color: #fff; text-decoration: none;" title="Close ThemeRoller"></a>'+
	      '<iframe name="trApp" src="http://jqueryui.com/themeroller/developertool/appinterface.php#'+hash+'" style="background: transparent; overflow: auto; width: 240px;height:100%;border: 0;" frameborder="0" ></iframe>'+
	      '</div>')
		.appendTo('body')
		.draggable({
		    start: function(){
			jq('<div id="div_cover" />').appendTo('#inline_themeroller').css({width: jq(this).width(), height: jq(this).height(), position: 'absolute', top: 0, left:0});
		    },
		    stop: function(){
			jq('#div_cover').remove();
		    },
		    opacity: 0.6,
		    cursor: 'move'
		})
		.resizable({
		    start: function(){
			jq(this).find('iframe').hide();
		    },
		    stop: function(){
			jq(this).find('iframe').show();
		    },
		    handles: 's'
		})
		.find('a.closeTR').click(function(){
		    closeThemeRoller();
		})
		.end()
		.find('.ui-resizable-s').css({
		    background: 'url(http://jqueryui.com/themeroller/developertool/icon_bookmarklet_dragger.gif) 50% 50% no-repeat',
		    border: 'none',
		    height: '14px',
		    dipslay: 'block',
		    cursor: 'resize-s',
		    bottom: '-3px'
		})
		.end()
		.css('cursor', 'move')
		.fadeIn();
	}
	reloadCSS();
    };
    //close dev tool
    var closeThemeRoller = function () {
	jq('#inline_themeroller').fadeOut();
    };
    //get current url hash
    var getHash = function () {
	var currSrc = window.location.hash;
	if (currSrc.indexOf('#') > -1) {
	    currSrc = currSrc.split('#')[1];
	}
	return currSrc;
    };
    //recursive reload call
    var reloadCSS = function(){
	var currSrc = getHash(), cssLink;
	if(jquitr.trString !== currSrc && currSrc !== ''){
	    jquitr.trString = currSrc;
	    cssLink = '<link href="http://jqueryui.com/themeroller/css/parseTheme.css.php?'+ currSrc +'" type="text/css" rel="Stylesheet" />';
	    //works for both 1.6 final and early rc's
	    if( jq("link[href*=parseTheme.css.php], link[href=ui.theme.css]").size() > 0){
		jq("link[href*=parseTheme.css.php]:last, link[href=ui.theme.css]:last").eq(0).after(cssLink);
	    } else {
		jq("head").append(cssLink);
	    }
	    if( jq("link[href*=parseTheme.css.php]").size() > 3){
		jq("link[href*=parseTheme.css.php]:first").remove();
	    }
	}
	window.setTimeout(reloadCSS, 1000);
    };
    // Actually add the roller
    addThemeRoller();
};

var callThemeroller = function(hash) {
    // give the current hash to the themeroller, so he can take the settings of the theme
    if (hash) {
     window.location.href += '#'+hash;
    }
    if (!/Firefox[\/\s](\d+\.\d+)/.test(navigator.userAgent)) {
        alert(sorry_only_firefox);
        return false;
    };

    wrapper(hash);
    jq('label[for=form.download]').parent().show();
};

var createDLDirectory = function() {
    document.location.href = 'portal_ui_tool/createDLDirectory';
};

// change the submit handler to include the hash of the themeroller theme
jq(document).ready(function() {
    // hide the download input - its only shown when themeroller opens
    jq('label[for=form.download]').parent().hide();

    // make the form "multiSubmitable"
    jq('input[name=form.actions.save]').addClass('allowMultiSubmit');

    jq('input[name=form.actions.save]').click(function() {
	var hash = jquitr.trString;
	var download_name = jq('input[name=form.download]').val();

	// a name was entered but no hash? thats not good!
	// mhh - but this could not happen in a perfect world
	if (download_name && !hash) {
            alert(nothing_themed);
	    return false;
	}

	// now the opposite: something was themed, but no download name given
	if (!download_name && hash) {
	    return window.confirm(name_missing);
	}

	// name validation
	if (download_name == 'sunburst') {
	    alert(no_sunburst_name);
	    return false;
	}

	if (download_name.match(/[a-z|0-9|_|-]*/) != download_name) {
	    alert(no_special_chars);
	    return false;
	}

	// if both are given, use it
	if (download_name && hash) {
	    jq('input[name=form.themeroller]').val(hash);
	}
    });
});
