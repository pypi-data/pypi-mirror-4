//-----------------------------------------------------------------------------
// j01.rating javascript
//-----------------------------------------------------------------------------
// Thanks to: Ritesh Agrawal, Karl Swedberg 

(function($) {
$.fn.j01Rater = function(settings) {
    settings = $.extend({
        fieldName: null,
        url: null,
        increment: 1,
        curvalue: 0
    }, settings);

    settings = $.extend({
        increment: (settings.increment < .75) ? .5 : 1
    }, settings);

    // conditions
    if (!settings.fieldName) {
        alert('j01Rater fieldName is missing');
    }
    if (!settings.url) {
        alert('j01Rater url is missing');
    }

    // setup rating wrapper
    var widget = $(this);
    var ratable = $('.ratable', widget);
    var average = $('.average', widget);

    // setup rating star and cancel wrapper
    var stars = ratable.children('.star');
    var cancel = ratable.children('.cancel');

    stars.mouseover(function(){
        event.drain();
        event.fill(this);
    })
    .mouseout(function(){
        event.drain();
        event.reset();
    })
    .focus(function(){
        event.drain();
        event.fill(this);
    })
    .blur(function(){
        event.drain();
        event.reset();
    });

    // setup click handler
    stars.click(function(){
        var key = getScoreKey($(this));
        if (settings.curvalue != key) {
            settings.curvalue = key
            rate(key);
        }
        return false;
    });

    // cancel button events
    if(cancel){
        cancel.mouseover(function(){
            event.drain();
            $(this).addClass('on');
        })
        .mouseout(function(){
            event.reset();
            $(this).removeClass('on');
        })
        .focus(function(){
            event.drain();
            $(this).addClass('on');
        })
        .blur(function(){
            event.reset();
            $(this).removeClass('on');
        })
        .click(function(){
            event.drain();
            var key = getScoreKey($(this));
            if (settings.curvalue != key) {
                settings.curvalue = key
                rate(key);
            }
            return false;
        });
    }

    // setup event handler
    var event = {
        fill: function(el){ // fill to the current mouse position.
            var index = stars.index(el) + 1;
            stars.children('a').css('width', '100%').end()
                 .slice(0, index).addClass('hover').end();
        },
        drain: function() { // drain all the stars.
            stars.filter('.on').removeClass('on').end()
                 .filter('.hover').removeClass('hover').end();
        },
        reset: function(){ // Reset the stars to the default index.
            stars.slice(0, settings.curvalue / settings.increment).addClass('on').end();
        }
    };
    //event.reset();

    function getScoreKey(ele) {
        return ele.children('a')[0].href.split('#')[1]
    }

    function renderResponse(response) {
        if (response.content) {
            var widgetParent = widget.parent();
            widgetParent.empty();
            widgetParent.html(response.content);
        }
    }

    function rate(key) {
	    var url = settings.url;
        var jsonProxy = getJSONRPCProxy(url);
        jsonProxy.addMethod('j01Rater', renderResponse);
        jsonProxy.j01Rater(settings.fieldName, key);
    }
    return(this);
};
})(jQuery);
