user_table_sql = """CREATE TABLE `user` (
`id`  int NOT NULL AUTO_INCREMENT ,
`username`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`password`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`isadmin`  tinyint(1) NOT NULL ,
`email`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
PRIMARY KEY (`id`),
  UNIQUE INDEX `user` (`username`) USING HASH
);"""

task_table_sql = """CREATE TABLE `timing` (
`id`  int NOT NULL AUTO_INCREMENT ,
`host_id`  int NOT NULL ,
`project_name`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`spider_name`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`last_time`  int(24) NOT NULL ,
`run_time`  float(64,0) NULL ,
PRIMARY KEY (`id`),
  UNIQUE INDEX `task` (`host_id`) USING HASH
);"""

host_table_sql = """CREATE TABLE `host` (
`id`  int NOT NULL AUTO_INCREMENT ,
`host`  varchar(24) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`name`  varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci NULL ,
`scrapyd_name`  varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NULL ,
`scrapyd_password`  varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NULL ,
`port`  int NOT NULL ,
`create_time`  int NOT NULL ,
`is_run`  tinyint(1) NOT NULL ,
PRIMARY KEY (`id`),
  UNIQUE INDEX `host` (`host`) USING HASH
);"""


project_sql = """CREATE TABLE `project` (
`id`  int NOT NULL AUTO_INCREMENT ,
`host_id`  int NULL ,
`project_name`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`description`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL ,
`create_time`  int NOT NULL ,
`update_time`  int NOT NULL ,
`project_path`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
`project_version`  varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
PRIMARY KEY (`id`)
)
;"""

sum_sql = [host_table_sql, task_table_sql, user_table_sql, project_sql]