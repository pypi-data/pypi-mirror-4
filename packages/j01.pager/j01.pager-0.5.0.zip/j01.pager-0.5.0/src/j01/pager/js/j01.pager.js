(function($) {
$.fn.j01Pager = function(o) {
    o = $.extend({
        resultExpression: '#j01PagerResult',
        methodName: 'getJ01PagerResult',
        url: '.',
        count: 5,
        start: 1,
        // sizes
        batchSize: 10,
        display: 5,
        // css colors
        bgColor: 'none',
        bgHoverColor: 'none',
        textColor: 'black',
        textHoverColor: 'red',
        // JS event handler
        onClick: doLoadContent,
        onAfterRender: false,
        onAfterSetResult: false,
        rotate: true,
        mouse: 'slide',
        // pager condition
        showPager: true,
        // order support
        sortName: false,
        sortOrder: false,
        // live search support
        searchWidgetExpression: false,
        minQueryLenght: 2,
        maxReSearch: 0,
        callback: setResult
    }, o || {});

    var outsidewidth_tmp = 0;
    var insidewidth = 0;
    var bName = navigator.appName;
    var bVer = navigator.appVersion;
    if(bVer.indexOf('MSIE 7.0') > 0) {
        var ver = "ie7";
    }
    var page = 1;
    var reSearchCounter = 0
    var currentPage = o.start;
    var currentSearchText = '';

    // livesearch support
    var loading = false;

    function setResult(response) {
        var content = response.content;
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
        reSearchCounter = 0;
        ele = $(o.resultExpression);
        ele.empty();
        ele.html(content);
        ele.show()
        if (o.onAfterSetResult){
            o.onAfterSetResult(ele);
        }
        loading = false;
    }

    // content loader with live search support
    function doLoadContent(page) {
        // supports search widget search string
        if (o.searchWidgetExpression) {
            searchText = $(o.searchWidgetExpression).val();
        }else {
            searchText = '';
        }
        // load only if not a request is pending
        if(!loading) {
            loading = true;
            currentSearchText = searchText;
            proxy = getJSONRPCProxy(o.url);
            proxy.addMethod(o.methodName, o.callback, o.requestId);
            proxy[o.methodName](page, o.batchSize, o.sortName, o.sortOrder, searchText);
        }
    }

    function doLiveSearch() {
        searchText = $(o.searchWidgetExpression).val();
        // search only if serchText is given
        if (!searchText) {
            // load again from start
            page = 1;
            loading = false;
            doLoadContent(page);
        }
        // search only if serchText is given
        if (searchText.length < o.minQueryLenght) {
            loading = false;
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

    function renderSearchWidget() {
        if (o.searchWidgetExpression) {
            // unbind previous event handler
            $(o.searchWidgetExpression).unbind('keyup');
            // now setup live search event handler
            $(o.searchWidgetExpression).bind('keyup', function(){
                doLiveSearch();
            });
        }
    }

    function renderPager(self) {
        if (!o.showPager) {
            // we only render the search widget
            return false;
        }
        if(o.display > o.count) {
            o.display = o.count;
        }
        self.empty();
        var aFirst = $(document.createElement('a')).html('First');
        var divFirst = $(document.createElement('div'));
        divFirst.addClass('first');

        if(o.rotate){
            var spanPrevious = $(document.createElement('span'));
            spanPrevious.addClass('previous').html('&laquo;');
            divFirst.append(aFirst).append(spanPrevious);
        }
        var divBatch = $(document.createElement('div'));
        divBatch.addClass('batch');
        var _ul = $(document.createElement('ul'));
        var c = (o.display - 1) / 2;
        var first = currentPage - c;
        var selobj;
        for(var i = 0; i < o.count; i++){
            var val = i+1;
            if(val == currentPage){
                var _obj = $(document.createElement('li'));
                _obj.html('<span class="current">'+val+'</span>');
                selobj = _obj;
                _ul.append(_obj);
            }else {
                var _obj = $(document.createElement('li'));
                _obj.html('<a>'+ val +'</a>');
                _ul.append(_obj);
                }               
        }       
        divBatch.append(_ul);
        var aLast = $(document.createElement('a')).html('Last');
        var divLast = $(document.createElement('div'));
        divLast.addClass('last');

        if(o.rotate){
            var spanNext = $(document.createElement('span'));
            spanNext.addClass('next').html('&raquo;');
            divLast.append(spanNext).append(aLast);
        }

        //append all:
        self.addClass('j01Pager');
        self.append(divFirst);
        self.append(divBatch);
        self.append(divLast);

        if(o.bgColor == 'none') {
            var a_css = {'color': o.textColor};
        }else {
            var a_css = {'color':o.textColor,'background-color':o.bgColor};
        }
        if(o.bgHoverColor == 'none') {
            var hover_css = {'color':o.textHoverColor};
        }else {
            var hover_css = {'color':o.textHoverColor, 'background-color':o.bgHoverColor};
        }  
        
        applyStyles(self, a_css, hover_css);
        applyWidth(self, _ul);
        //calculate width of the ones displayed
        var outsidewidth = outsidewidth_tmp - aFirst.parent().width() -3;
        /*
        if(ver == 'ie7'){
            divBatch.css('width', outsidewidth+72+'px');
            divLast.css('left', outsidewidth_tmp+6+72+'px');
        }else {
            divBatch.css('width', outsidewidth+'px');
            divLast.css('left', outsidewidth_tmp+6+'px');
        }
        */
        // is seems that not only ie7 needs more space
//        divBatch.css('width', outsidewidth+72+'px');
//        divLast.css('left', outsidewidth_tmp+6+72+'px');
        divBatch.css('max-width', outsidewidth+'px');
        divLast.css('left', outsidewidth_tmp+6+'px');
        if(o.rotate){
            spanNext.hover(
                function() {
                  thumbs_scroll_interval = setInterval(
                    function() {
                      var left = divBatch.scrollLeft() + 1;
                      divBatch.scrollLeft(left);
                    },
                    20
                  );
                },
                function() {
                  clearInterval(thumbs_scroll_interval);
                }
            );
            spanPrevious.hover(
                function() {
                  thumbs_scroll_interval = setInterval(
                    function() {
                      var left = divBatch.scrollLeft() - 1;
                      divBatch.scrollLeft(left);
                    },
                    20
                  );
                },
                function() {
                  clearInterval(thumbs_scroll_interval);
                }
            );
            if(o.mouse == 'press'){
                spanNext.mousedown(
                    function() {
                      thumbs_mouse_interval = setInterval(
                        function() {
                          var left = divBatch.scrollLeft() + 5;
                          divBatch.scrollLeft(left);
                        },
                        20
                      );
                    }
                ).mouseup(
                    function() {
                      clearInterval(thumbs_mouse_interval);
                    }
                );
                spanPrevious.mousedown(
                    function() {
                      thumbs_mouse_interval = setInterval(
                        function() {
                          var left = divBatch.scrollLeft() - 5;
                          divBatch.scrollLeft(left);
                        },
                        20
                      );
                    }
                ).mouseup(
                    function() {
                      clearInterval(thumbs_mouse_interval);
                    }
                );
            }else {
                spanPrevious.click(function(e){
                    var width = outsidewidth - 10;
                    var left = divBatch.scrollLeft() - width;
                    divBatch.animate({scrollLeft: left +'px'});
                }); 
                
                spanNext.click(function(e){
                    var width = outsidewidth - 10;
                    var left = divBatch.scrollLeft() + width;
                    divBatch.animate({scrollLeft: left +'px'});
                });
            }
        }

        //first and last:
        aFirst.click(function(e){
            divBatch.animate({scrollLeft: '0px'});
            divBatch.find('li').eq(0).click();
        });
        aLast.click(function(e){
            divBatch.animate({scrollLeft: insidewidth +'px'});
            divBatch.find('li').eq(o.count - 1).click();
        });

        //click a page
        divBatch.find('li').click(function(e){
            selobj.html('<a>'+selobj.find('.current').html()+'</a>'); 
            page = $(this).find('a').html();
            $(this).html('<span class="current">'+page+'</span>');
            selobj = $(this);
            applyStyles($(this).parent().parent().parent(), a_css, hover_css);
            applyWidth($(this).parent().parent().parent(), _ul);     
            var left = (this.offsetLeft) / 2;
            var tmp = left - (outsidewidth / 2);
            if(ver == 'ie7') {
                divBatch.animate({scrollLeft: left + tmp - aFirst.parent().width() + 35 +'px'});
            }else {
                divBatch.animate({scrollLeft: left + tmp - aFirst.parent().width() + 'px'});
            }
            o.onClick(page);
        });
        
        var last = divBatch.find('li').eq(o.start-1);
        var offset = last.offset();
        try {
             var left = offset.left / 2;
        } catch (e) {
            var left = 0;
        } 
        var tmp = left - (outsidewidth / 2);
        if(ver == 'ie7'){
             divBatch.animate({scrollLeft: left + tmp - aFirst.parent().width() + 35 + 'px'});
        }else {
            divBatch.animate({scrollLeft: left + tmp - aFirst.parent().width() + 'px'});
        }
    }

    function applyStyles(obj, a_css, hover_css){
        obj.find('a').css(a_css);
        obj.find('span.current').css(hover_css);
        obj.find('a').hover(
        function(){
            $(this).css(hover_css);
        },
        function(){
            $(this).css(a_css);
        });
    }

//    function applyWidth(obj, _ul){
//        insidewidth = 8;
//        obj.find('li').each(function(i, n) {
//            if(i == (o.display-1)){
//                // last item
//                //outsidewidth_tmp = $(this).offset().left + this.offsetWidth;
//                outsidewidth_tmp = insidewidth + this.offsetWidth + 60;
//            }
//            insidewidth += this.offsetWidth;
//        });
//        _ul.css('width', insidewidth+'px');
//    }

    // fix this, we have troubles to get the offsetWidth in j01.dialog
    function applyWidth(obj, _ul){
        insidewidth = 8;
        obj.find('li').each(function(i, n) {
            w = this.offsetWidth;
            if (!w) {
                w = 25;
            }
            if(i == (o.display-1)){
                // last item
                //outsidewidth_tmp = $(this).offset().left + this.offsetWidth;
                outsidewidth_tmp = insidewidth + w + 60;
            }
            insidewidth += w;
        });
        _ul.css('width', insidewidth+'px');
    }

    return this.each(function(){
        renderSearchWidget();
        renderPager($(this));
        if (o.onAfterRender){
            o.onAfterRender($(this));
        }
    });
};
})(jQuery);
