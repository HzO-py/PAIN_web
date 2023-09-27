!function($){
    var MMPaginator = function(element, options){
        this.$el = $(element);
        this.opts = options;
    };

    MMPaginator.prototype = {
        _initLayout: function(){
            var that = this;
            var $el = this.$el;
            var opts = this.opts;

            $el.addClass("mmPaginator");
            var pgHtmls = [
                '<div class="totalCountLabel"></div>',
                '<ul class="pageList"></ul>',
                '<div class="limit"><select></select></div>'
            ];
            $el.append($(pgHtmls.join('')));

            this.$totalCountLabel = $el.find('.totalCountLabel');
            this.$pageList = $el.find('.pageList');
            this.$limitList = $el.find('.limit select');
            this.$keywords = document.getElementById('keyinput');
            this.$group = document.getElementById('allgroupselect');
            this.$allquestion = document.getElementById('allquestion');
            this.$allsetquestion = document.getElementById('allsetquestion');
            this.$allcom = document.getElementById('allcom');

             var $limitList = this.$limitList;
            $.each(opts.limitList, function(){
                var $option = $('<option></option>')
                    .prop('value',this)
                    .text(that.formatString(opts.limitLabel,[this]));
                $limitList.append($option);
            });
            var $option = $('<option></option>')
                    .prop('value','99999')
                    .text('展示所有');
            $limitList.append($option);
            $limitList.on('change', function(){
                $el.data('page', 1);
                that.$mmGrid.load();
            });

        }

        , _plain: function(page, totalCount, limit){
            var that = this;
            var $el = this.$el;
            var $pageList = this.$pageList;
            var totalPage = totalCount % limit === 0 ? parseInt(totalCount/limit) : parseInt(totalCount/limit) + 1;
            totalPage = totalPage ? totalPage : 0;
            if(totalPage === 0){
                page = 1;
            }else if(page > totalPage){
                page = totalPage;
            }else if(page < 1 && totalPage != 0){
                page = 1;
            }
            //
            var $prev = $('<li class="prev"><a>«</a></li>');
            if(page<=1){
                $prev.addClass('disable');
            }else{
                $prev.find('a').on('click', function(){
                    $el.data('page', page-1);
                    that.$mmGrid.load();
                });
            }
            $pageList.append($prev);
            /////
            var list = [1];
            if(page > 4 ){
                list.push('...');
            }
            for(var i= 0; i < 5; i++){
                var no = page - 2 + i;
                if(no > 1 && no <= totalPage-1){
                    list.push(no);
                }
            }
            if(page+1 < totalPage-1){
                list.push('...');
            }
            if(totalPage>1){
                list.push(totalPage);
            }
            $.each(list, function(index, item){
                var $li = $('<li><a></a></li>');
                if(item === '...'){
                    $li.addClass('').html('...');
                }else if(item === page){
                    $li.addClass('active').find('a').text(item);
                }else{
                    $li.find('a').text(item).prop('title','第'+item+'页').on('click', function(e){
                        $el.data('page', item);
                        that.$mmGrid.load();
                    });
                }
                $pageList.append($li);
            });
            //
            var $next = $('<li class="next"><a title="下一页">»</a></li>');
            if(page>=totalPage){
                $next.addClass('disable');
            }else{
                $next.find('a').on('click', function(){
                    $el.data('page', page+1);
                    that.$mmGrid.load();
                });
            }
            $pageList.append($next);
            if($('th .checkAll').is(":checked")){
                $('th .checkAll').prop('checked','');
            }

        }

        , _search: function(page, totalCount, limit){

        }

        , load: function(params){
            var selectList = [];
            localStorage.setItem('selectList',JSON.stringify(selectList))
            var allselectList = [];
            localStorage.setItem('allselectList',JSON.stringify(allselectList))
            var $el = this.$el;
            var $limitList = this.$limitList;
            var opts = this.opts;
            var page = params[opts.pageParamName];
            if(page === undefined || page === null){
                page = $el.data('page');
            }
            $el.data('page', page);
            // console.log(89888,$el.data())
            var totalCount = params[opts.totalCountName];
            if(totalCount === undefined){
                totalCount = 0;
            }
            $el.data('totalCount', totalCount);
            // console.log(params)
            var limit = params[opts.limitParamName];
            if(!limit){
                limit = $limitList.val();
            }
            this.$limitList.val(limit);

            this.$totalCountLabel.html(this.formatString(opts.totalCountLabel,[totalCount]));
            this.$pageList.empty();

            this._plain(page, totalCount, this.$limitList.val());

            // if(this.$mmGrid.opts.indexCol){
            //     var indexCol = this.$mmGrid.opts.cols[0];
            //     indexCol.renderer = function(val,item,rowIndex){
            //         console.log(9999,params[opts.pageParamName])
            //         return '<label class="mmg-index">' +
            //             (rowIndex + 1 + ((params[opts.pageParamName]-1) * params[opts.limitParamName])) +
            //             '</label>';
            //     };
            // }

        }

        , formatString: function(text, args){
            return text.replace(/{(\d+)}/g, function(match, number) {
                return typeof args[number] != 'undefined'
                    ? args[number]
                    : match
                    ;
            });
        }

        , params: function(){
            var opts = this.opts;
            var $el = this.$el;
            var $limitList = this.$limitList;
            var $keywords = this.$keywords;
            var $group = this.$group;
            var $allquestion = this.$allquestion;
            var $allsetquestion = this.$allsetquestion;
            var $allcom = this.$allcom;

            var params = {};
            params[opts.pageParamName] = $el.data('page');
            params[opts.limitParamName] = $limitList.val();
            if($keywords)
                params[opts.keywordsName] = $keywords.value;
            if($group) {
                index = $group.selectedIndex;
                params['gid'] = $group.options[index].value;//0所有分组 -1未分类
            }
            if($allquestion) {
                index = $allquestion.selectedIndex;
                params['qid'] = $allquestion.options[index].value;//0所有 1已完成 2答题中 3未答题
            }
            if($allsetquestion) {
                index = $allsetquestion.selectedIndex;
                params['sid'] = $allsetquestion.options[index].value;//0所有 1已分配 2未分配
            }
            if($allcom) {
                index = $allcom.selectedIndex;
                params['cid'] = $allcom.options[index].value;//子公司id
            }
            return params;
        }

        , init: function($grid){
            var that = this;
            var opts = that.opts;
            this.$mmGrid = $grid;
            this._initLayout();
            this.$mmGrid.on('loadSuccess', function(e, data){
                var params = {};
                params[that.opts.totalCountName] = data[that.opts.totalCountName];
                params[that.opts.pageParamName] = data[that.opts.pageParamName];
                params[that.opts.limitParamName] = data[that.opts.limitParamName];
                that.load(params);
            });
            var params = {};
            params[opts.totalCountName] = 0;
            params[opts.pageParamName] = opts.page;
            params[opts.limitParamName] = opts.limit;
            this.load(params);

            if($grid.opts.indexCol){
                var indexCol = $grid.opts.cols[0];
                indexCol.renderer = function(val,item,rowIndex){
                    var params = that.params();
                    // console.log(params)
                    return '<label class="mmg-index">' +
                        (rowIndex + 1 + ((params[opts.pageParamName]-1) * params[opts.limitParamName])) +
                        '</label>';
                };
            }

        }

    };

    $.fn.mmPaginator = function(){

        if(arguments.length === 0 || typeof arguments[0] === 'object'){
            var option = arguments[0]
                , data = this.data('mmPaginator')
                , options = $.extend(true, {}, $.fn.mmPaginator.defaults, option);
            if (!data) {
                data = new MMPaginator(this[0], options);
                this.data('mmPaginator', data);
            }
            return $.extend(true, this, data);
        }
        if(typeof arguments[0] === 'string'){
            var data = this.data('mmPaginator');
            var fn =  data[arguments[0]];
            if(fn){
                var args = Array.prototype.slice.call(arguments);
                return fn.apply(data,args.slice(1));
            }
        }
    };

    $.fn.mmPaginator.defaults = {
         style: 'plain'
        , totalCountName: 'totalCount'
        , page: 1
        , pageParamName: 'page'
        , limitParamName: 'limit'
        , limitLabel: '每页{0}条'
        , totalCountLabel: '共<span>{0}</span>条记录'
        , limit: undefined
        , limitList: [20, 30, 40, 50]
        , keywordsName: 'keyword'
        , groupNname:'group'
    };

    $.fn.mmPaginator.Constructor = MMPaginator;

}(window.jQuery);