Option.Internationalization = 'CN';

language = {
    CN: {
        home: "首页",
        server: "服务器",
        project: "项目管理",
        server_domain: "服务器域名",
        server_name: "服务器名称",
        create_time: "创建时间",
        server_state: "服务器状态",
        option: "选项",
        add_new_server: "添加服务器",
        delete_server: "删除服务器",
        delete_server_project: "删除服务器项目",
        schedul: "调度",
        config: "配置",
        ssh: "ssh",
        project_name: "项目名称",
        description: "描述",
        update_time: "更新时间",
        deploy: "部署",
        delete: "删除",
        edit: "编辑",
        add_project: "添加项目",
        spider_name: "蜘蛛名称",
        scrapy_base_model: "scrapy 基础类",
        start_url: "初始url",
        save: "保存",
        cancel: "取消",
        deploy_server: "部署至服务器",
        submit: "提交",
        back: "返回",
        start_time: "开始时间",
        end_time: "结束时间",
        runing: "运行",
        stop: "停止",
        set_task_run_interval: "设置蜘蛛运行间隔时间(秒)"
    },
    EN : {
        home: "Home",
        server: "Server",
        project: "Project",
        server_domain: "Server domain",
        server_name: "Server name",
        create_time: "Create time",
        server_state: "Server state",
        option: "Option",
        add_new_server: "Add server",
        delete_server: "Delete server",
        delete_server_project: "Delete server project",
        schedul: "Schedul",
        config: "Config",
        ssh: "Ssh",
        project_name: "Project name",
        description: "Description",
        update_time: "Update time",
        deploy: "Deploy",
        delete: "Delete",
        edit: "Edit",
        add_project: "Add project",
        spider_name: "Spider name",
        scrapy_base_model: "Scrapy base model",
        start_url: "Start url",
        save: "Save",
        cancel: "Cancel",
        deploy_server: "Delpoy",
        submit: "Submit",
        back: "Back",
        start_time: "Start time",
        end_time: "End time",
        runing: "Runing",
        stop: "Stop",
        set_task_run_interval: "Set spider run interval"
    }
};



function on_Translation(){
    // 默認是CN
    // 默認調用每一個
    if (Option.Internationalization == 'CN'){
        Option.Internationalization = 'EN';
    }else if (Option.Internationalization == 'EN'){
        Option.Internationalization = 'CN';
    }
    // 調用每一個頁面的專用翻譯程序
    Translation_this(Option.Internationalization);
}