(function($) {
$.fn.j01Scroller = function(o) {
    o = $.extend({
        scrollerName: 'j01Scroller',
        methodName: 'getJ01ScrollerResult',
        url: '.',
        // position
        offset: 20,
        // sizes
        batchSize: 10,
        // JS event handler
        onAfterSetResult: false,
        // order support
        sortName: false,
        sortOrder: false,
        // cache
        cacheKey: null,
        cacheExpireMinutes: 5,
        // live search support
        searchWidgetExpression: false,
        minQueryLenght: 2,
        maxReSearch: 0,
        callback: setResult
    }, o || {});

    var container = null;
    var page = 1;
    var currentSearchText = '';
    var loading = false;
    var scroller = false;
    var useLocalStorage = false;

    try {
        if (o.cacheKey && 'localStorage' in window && window['localStorage'] !== null) {
            useLocalStorage = true;
        }
    } catch (e) {}


    function setResult(response) {
        var content = response.content;
        var more = response.more;
        searchText = $(o.searchWidgetExpression).val();
        if (searchText && currentSearchText != searchText) {
            // search again
            if (reSearchCounter < o.maxReSearch) {
                reSearchCounter += 1;
                doLiveSearch();
            }
            loading = false;
            return false;
        }
        container.append(content);
        if (o.onAfterSetResult){
            o.onAfterSetResult(container);
        }
        doCacheData(content);
        // reset loader
        loading = false;
        if (more) {
            // only reset scroller if more content is available, otherwise
            // let the scroller as is (true) which will block from processing
            // see: setUpHandler and checkScroller
            scroller = false;
        }
    }

    function doLiveSearch() {
        searchText = $(o.searchWidgetExpression).val();
        // search only if serchText is given
        if (!searchText) {
            // load again from start
            page = 1;
            loading = false;
            doLoadContent();
        }
        // search only if serchText is given
        if (searchText.length < o.minQueryLenght) {
            loading = false;
            scroller = false;
            return false;
        }
        // load only if not a request is pending and there is not cache 
        if(!loading) {
            // reset page
            page = 1;
            loading = true;
            // set current search text
            currentSearchText = searchText;
            var proxy = getJSONRPCProxy(o.url);
            proxy.addMethod(o.methodName, o.callback, o.requestId);
            // we always use 1 as page value, we only need a page larger then 1
            // if we call the livesearch with a batch
            proxy[o.methodName](page, o.batchSize, o.sortName, o.sortOrder, searchText);
        }
    }

    function setUpSearchWidget() {
        if (o.searchWidgetExpression) {
            // unbind previous event handler
            $(o.searchWidgetExpression).unbind('keyup');
            // now setup live search event handler
            $(o.searchWidgetExpression).bind('keyup', function(){
                doLiveSearch();
            });
        }
    }

    // content loader with search support
    function doLoadContent() {
        // load only if not a request is pending
        if(!loading) {
            // supports search widget search string
            if (o.searchWidgetExpression) {
                searchText = $(o.searchWidgetExpression).val();
            }else {
                searchText = '';
            }
            page += 1;
            loading = true;
            currentSearchText = searchText;
            proxy = getJSONRPCProxy(o.url);
            proxy.addMethod(o.methodName, o.callback, o.requestId);
            proxy[o.methodName](page, o.batchSize, o.sortName, o.sortOrder, searchText);
        }
    }

    function saveData(key, value) {
        if (useLocalStorage) {
            try {
                localStorage.setItem(key, value);
            }catch(e) {}
        }
    }

    function getData(key) {
        if (useLocalStorage) {
            try {
                return localStorage.getItem(key);
            }catch(e) {}
        }
    }

    function removeData() {
        if (useLocalStorage) {
            try {
                localStorage.removeItem(key);
            }catch(e) {}
        }
    }

    function doClearData() {
        if (useLocalStorage) {
            var timestamp = Number(new Date());
            var old = localStorage.getItem(o.cacheKey + '-time');
            var diff = timestamp - old;
            diff = Math.round(diff/1000/60);
            if(diff >= o.cacheExpireMinutes) {
                localStorage.removeItem(o.cacheKey + '-time');
                localStorage.removeItem(o.cacheKey + '-page');
                localStorage.removeItem(o.cacheKey + '-content');
            }
        }
    }

    function doCacheData(content) {
        // cache data
        if (useLocalStorage) {
            var old = getData(o.cacheKey + '-content');
            if(old === null) {
                old = "";
            }
            saveData(o.cacheKey + '-content', old + content);
            saveData(o.cacheKey + '-page', page);
            var timestamp = Number(new Date());
            saveData(o.cacheKey + '-time', timestamp);
        }
    }

    function setUpData() {
        if (useLocalStorage) {
            // clear cache if expired
            doClearData();
            try {
                var content = getData(o.cacheKey + '-content');
                if(content != undefined) {
                    page = parseInt(getData(o.cacheKey + '-page'));
                    container.html(content);
                    if (o.onAfterSetResult){
                        o.onAfterSetResult(container);
                    }
                }
            } catch (e) {}
        }
    }

    function checkScroller() {
        // check position
        var scroll = $(window).scrollTop();
        var height = $(document).height() - $(window).height() - o.offset;
        if (scroll > height) {
            // set true as scroller (prevents future checkScroller call)
            scroller = true;
            // load content
            doLoadContent();
        }
    }

    function setUpHandler() {
        var self = this;
        $(window).scroll(function() {
            if (!scroller) {
                // set scroller name as scroller
                scroller = o.scrollerName;
            }
         });
        setInterval(function() {
            if (scroller == o.scrollerName) {
                checkScroller();
            }
         }, 250);
    }

    return this.each(function(){
        container = $(this);
        setUpSearchWidget();
        setUpData();
        setUpHandler();
    });
};
})(jQuery);
