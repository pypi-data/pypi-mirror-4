//-----------------------------------------------------------------------------
// j01.autosuggest javascript
//-----------------------------------------------------------------------------

(function($) {
$.fn.j01AutoSuggest = function(settings) {
    o = $.extend({
        formName: null,
        fieldName: null,
        url: null,
        jsonRPCMethodName: 'j01AutoSuggest',
        widgetExpression: '.j01AutoSuggestWidget',
        inputExpression: '.j01AutoSuggestInput',
        resultExpression: '.j01AutoSuggestResult',
        resultContainerExpression: '.j01AutoSuggestContainer',
        requestId: 'j01LiveList',
        callback: j01RenderAutoSuggestResult,
        minQueryLenght: 1,
        fadeOutTimeout: 100,
        showAllOnClick: false
    }, settings);

    var widgetElement = $(o.widgetExpression, this);
    var inputElement = $(o.inputExpression, this);
    var box = null;

    var loading = false;
    var searchText = false;
    var current = null;

    var KEY = {
        BACK: 8,
        DEL: 46,
        DOWN: 40,
        ESC: 27,
        PAGEDOWN: 34,
        PAGEUP: 33,
        ENTER: 13,
        TAB: 9,
        UP: 38
    };

    function doIterate(action) {
        if(box){
            i = 0;
            box.find("li").each(function(){
                if($(this).attr("class") == "selected")
                i = 1;
            });
            if(i == 1) {
                var sel = box.find("li[class='selected']");
                if(action == 'down') {
                    sel.next().addClass("selected");
                }else{
                    sel.prev().addClass("selected");
                }
                sel.removeClass("selected");
            }else{
                if(action == 'down') {
                    box.find("li:first").addClass("selected");
                }else{
                    box.find("li:last").addClass("selected");
                }
            }
        }
    }

    function doSelect(action) {
        if(box){
            var sel = box.find("li[class='selected']");
            inputElement.val(sel.text());
            clearBox();
        }
    }

    function doKeyTrack(event) {
        // track last key pressed if event is given
        
        if (event) {
            switch(event.which) {
                case KEY.TAB:
                    clearBox();
                    event.preventDefault();
                    return false;
   
                case KEY.DOWN:
                    doIterate('down');
                    event.preventDefault();
                    return false;
    
                case KEY.UP:
                    doIterate('up');
                    event.preventDefault();
                    return false;
    
                case KEY.ENTER:
                    doSelect();
                    event.preventDefault();
                    return false;
            }
            if (event.which != 39 && event.which != 37 && event.which != 38 && event.which != 40 && event.which != 13 && event.which != 9 ) {
                doSearch();
            }
        }
    }

    function clearBox(){
        // remove eventhandler and box
        var box = $(".j01AutoSuggestBox", widgetElement);
        box.delay(o.fadeOutTimeout).fadeOut();
        box.remove();
    }

    function j01RenderAutoSuggestResult(response) {
        if (response.items) {
            clearBox();
            var lis = '';
            for (var i=0;i<response.items.length;i++) {
               lis += '<li>' + response.items[i] + '</li>';
            }
            // setup box, ul and li
            box = $('<div class="j01AutoSuggestBox"><ul>'+lis+'</ul></div>')
            widgetElement.append(box);
            $(".j01AutoSuggestBox > ul li", widgetElement.get(0)).live('mouseover', function() {    
                current = $(this).parent().find("li[class='selected']").removeClass('selected');
                $(this).addClass('selected');
            });
            
            // show result
            box.width(widgetElement.width());
            box.fadeIn();
            // apply select on click
            $(".j01AutoSuggestBox > ul li", widgetElement.get(0)).live('click', function() {
                inputElement.val($(this).text());
                clearBox();
            });
            // apply cleanup on blur
            widgetElement.live('blur', function(){
                if (!$(this).parent('.j01AutoSuggestBox')) {
                    clearBox();
                }
            });
        }
        loading = false;
    }

    function doSearch() {
        searchText = inputElement.val();
        // search only if searchText is given
        if (searchText == '' || searchText.length < o.minQueryLenght) {
            return false;
        }
        // load only if not a request is pending and page not higher then last 
        // page
        if(!loading) {
            var proxy = getJSONRPCProxy(o.url);
            loading = true;
            proxy.addMethod(o.jsonRPCMethodName, o.callback, o.requestId);
            proxy[o.jsonRPCMethodName](o.formName, o.fieldName, searchText);
        }
    }

    function showAllOnClick() {
        if ($(".j01AutoSuggestBox", widgetElement).length) {
            // remove box on second click
            clearBox();
            return false;
        }
        if(!loading && o.showAllOnClick) {
            // search all items with empty searchText or whatever your
            // implementation returns without en empty string
            searchText = '';
            var proxy = getJSONRPCProxy(o.url);
            loading = true;
            proxy.addMethod(o.jsonRPCMethodName, o.callback, o.requestId);
            proxy[o.jsonRPCMethodName](o.formName, o.fieldName, searchText);
        }
    }

    return this.each(function(){
        $(this).keyup(function(event){
            doKeyTrack(event);
            return false;
        });
        if (o.showAllOnClick) {
            inputElement.click(function(){
                showAllOnClick();
                return false;
            });
        }
    });
};
})(jQuery);
