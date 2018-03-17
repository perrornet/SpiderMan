String.prototype.format=function(b){var a=this;if(arguments.length>0){if(arguments.length==1&&typeof(b)=="object"){for(var d in b){if(b[d]!=undefined){var e=new RegExp("({"+d+"})","g");a=a.replace(e,b[d])}}}else{for(var c=0;c<arguments.length;c++){if(arguments[c]!=undefined){var e=new RegExp("({["+c+"]})","g");a=a.replace(e,arguments[c])}}}}return a};
$.ajaxSetup({
    error: function(jqXHR, textStatus, errorThrown) {
        var status = 0;
        switch (jqXHR.status) {
        case(500):
            $.message({
                message:
                "{msg}".format({
                    msg:
                    jqXHR.responseJSON.msg
                }),
                type: "error",
                time: 5000
            });
            break;
        case (400):
            $.message({
                message:
                "{msg}".format({
                    msg:
                    jqXHR.responseJSON.msg
                }),
                type: "error",
                time: 5000
            });
            break;
        case (404):
            $.message({
                message:
                "{msg}".format({
                    msg:
                    jqXHR.responseJSON.msg
                }),
                type: "error",
                time: 5000
            });
            break;
        default:
            $.message({
                message:
                "{msg}".format({
                    msg:jqXHR.responseJSON.msg
                }),
                type: "error",
                time: 5000
            });
            break;
        }
    }
});function sleep(n) {
            var start = new Date().getTime();
            while (true) if (new Date().getTime() - start > n) break;
        }
function GetQueryString(name){var reg=new RegExp("(^|&)"+name+"=([^&]*)(&|$)");var r=window.location.search.substr(1).match(reg);if(r!=null){return unescape(r[2])}return null};


Option.host_list_url =      '/api/web/Host/';
Option.new_host_url =      '/api/web/Host/newHost/';
Option.host_ssh_url =       '/html/Host/{host_id}/WebSshIndex/';
Option.api_host_ssh_url =   '/api/web/Host/{host_id}/host_shh/';
Option.file_code_url =      '/api/web/NewProject/file_code/';
Option.update_file_url =    '/api/web/Project/{project_id}/update_file/{file_name}/';
Option.modify_Conf_url =    '/api/web/Host/{host_id}/modify_Conf/';
Option.delete_host_url =    '/api/web/Host/{host_id}/delete_host/';
Option.list_project_url =   '/api/web/Host/{host_id}/list_project/';
Option.scrapy_file_url =    '/api/web/Project/scrapy_file/{project_id}/';
Option.location_list_project_url = '/api/web/Project/list_project/';
Option.start_project_url =  '/api/web/Project/start_project/';
Option.location_list_spider_py_url =  '/api/web/Project/{project_id}/list_spider/';
Option.edit_scrapy_file_url =  '/html/Project/{project_id}/edit_file/';
Option.get_file_url =  '/api/web/Project/{project_id}/file_code/{file_name}/';
Option.delete_location_project_url =  '/api/web/Project/delete_project/{project_name}/';
Option.deploy_project_url =  '/api/web/Project/deploy_project/{host_id}/{project_id}/';
Option.stop_spider_url =    '/api/web/Host/{host_id}/project/{project_name}/Stop_spider/{job_id}/';
Option.list_job_url =       '/api/web/Host/{host_id}/project/{project_name}/list_job/';
Option.list_spider_url =    '/api/web/Host/{host_id}/project/{project_name}/list_spider/';
Option.delete_project_url = '/api/web/Host/{host_id}/project/{project_name}/delete_project/';
Option.run_spider_url =     '/api/web/Host/{host_id}/project/{project_name}/run_spider/{spider_name}/';
Option.cancel_spider_url =  '/api/web/Host/{host_id}/project/{project_name}/spider_cancel/{spider_name}/';
Option.set_timing_spider_url =  '/api/web/Host/{host_id}/Project/{project_name}/timing_spider/{spider_name}/{time}/';
Option.get_timing_spider_url =  '/api/web/Host/{host_id}/Project/{project_name}/get_timing_spider/{spider_name}/';
Option.spider_log_url =     '/api/web/Host/{host_id}/project/{project_name}/spider_log/{spider_name}/{spider_id}/';
