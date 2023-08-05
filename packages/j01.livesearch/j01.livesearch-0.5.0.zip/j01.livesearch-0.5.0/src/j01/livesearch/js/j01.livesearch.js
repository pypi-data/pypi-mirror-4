(function($) {
$.fn.j01LiveSearch = function(p) {
    p = $.extend({
        resultExpression: '#j01LiveSearchResult',
        methodName: 'getJ01LiveSearchResult',
        url: null,
        minQueryLenght: 2,
        cacheResults: true,
        requestId: 'j01LiveSearch',
        callback: setLiveSearchResult,
        onAfterRender: null
    }, p || {});

    var searchInputElement = false;
    var searchText = false;
    var currentSearchText = null;
    var cacheData = {};
    var initialData = '';
    var loading = false;

    function resetLiveSearch() {
        loading = false;
    }

    function setLiveSearchResult(response) {
        var content = response.content;
    	if (!searchText && p.cacheResults) {
    	    // use initial data as content
    	    content = initialData;
        }
        if (searchText != currentSearchText) {
            // search again
            loading = false;
            doLiveSearch();
            return false;
        }
        ele = $(p.resultExpression);
        ele.empty();
        ele.html(content);
        ele.show()
        loading = false;
        // store search results if cache enabled
        if (p.cacheResults) {
            cacheData[searchText] = content;
        }
        if (p.onAfterRender){
            p.onAfterRender();
        }
    }

    function doLiveSearch() {
        // use stored search results if available
        if (p.cacheResults) {
            for (var k in cacheData) {
                if (k == searchText) {
                    ele = $(p.resultExpression);
                    ele.html(cacheData[k])
                    ele.show()
                    loading = false;
                    return false;
                }
            }
        }
        // search only if serchText is given
    	if (!searchText) {
    	    ele = $(p.resultExpression);
    	    ele.html(initialData);
            ele.show();
            loading = false;
            return false;
        }
        // search only if serchText is given
    	if (searchText.length < p.minQueryLenght) {
            loading = false;
            return false;
        }
        // load only if not a request is pending and there is not cache 
        if(!loading) {
        	var proxy = getJSONRPCProxy(p.url);
            loading = true;
        	proxy.addMethod(p.methodName, p.callback, p.requestId);
        	// do livesearch call
        	currentSearchText = searchText
        	proxy[p.methodName](searchText);
        }
    }

    return this.each(function(){
        if (p.cacheResults) {
            initialData = $(p.resultExpression).html()
        }
        $(this).keyup(function(){
            searchInputElement = $(this);
        	searchText = $(this).val();
        	doLiveSearch();
        });
    });
};
})(jQuery);
