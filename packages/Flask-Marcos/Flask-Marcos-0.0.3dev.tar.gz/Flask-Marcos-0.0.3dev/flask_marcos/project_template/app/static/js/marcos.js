$(function(){



    $.extend($.jgrid.defaults, {
        /*Parsea el GET request de jqgrid para que pueda ser interpretado por
        * Flask_Restless del lado del servidor*/
        serializeGridData: function(postData){

            parsedPostData = new Object()
            query = {}

            query['order_by'] = [{'field':postData.sidx, 'direction':postData.sord}];

            if (postData.filters) {
                filters = $.parseJSON(postData.filters);
                filterDic = [];

                $.each(filters.rules, function(k, v){
                    rules = {};
                    rules['name'] = v['field'];

                    switch(v['op']){
                        case 'cn':
                            rules['op'] = 'like';
                            rules['val'] = '%'+v['data']+'%'
                            break;
                        case 'cn':
                            rules['op'] = 'like'
                            rules['val'] = v['data']+'%'
                            break;
                        case 'cn':
                            rules['op'] = 'like'
                            rules['val'] = '%'+v['data']
                            break;
                        default:
                            rules['op'] = v['op']
                            rules['val'] = v['data']
                    };
                    filterDic.push(rules)
                });
                query['filters'] = filterDic;
            };


            parsedPostData.q = JSON.stringify(query);
            parsedPostData.page = postData.page
            parsedPostData.results_per_page = postData.rows


            delete postData
            return parsedPostData
        }
    });

    /*asigna la funcion para crear el mudulo en nuevo tab apartir del
    * link creado de forma dinamica en el template por el modulo iniciado*/
   $(".icon.upleft a").click(openModule);
});

function log(obj){
    console.log(obj)
}

function openModule(){
    tabId = $(this).attr("data-id");
    moduleUrl= $(this).attr("data-target")
    $("#mainTab li.active").removeClass("active");
    $(".tab-content .active").removeClass("active");
    $("#mainTab").append("<li class='active'><a data-toggle='tab' href='#"+tabId+"'><span class='small "+$(this).attr("data-icon")+"'></span>"+$(this).attr("data-label")+"</a></li>");
    $("#mainTabContent").append("<div class='tab-pane container active' id='"+tabId+"'></div>");
    $.get(moduleUrl, function(data){
        $("#"+tabId).html(data);
    });
    return false;
};

