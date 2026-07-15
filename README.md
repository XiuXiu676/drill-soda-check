#### 一、Drill部署

##### 1. 下载并解压，演示版本为1.22.0

##### 2. 确认Java环境，Drill1.22.0不支持Java8，推荐Java11、Java17或Java21

##### 3. 启动Drill服务：bin/drill-embedded.bat

##### 4. 打开网页配置界面：localhost:8047

##### 5. 添加数据源：Storage->Create->Configuration

MySQL示例：
```
{
  "type": "jdbc",
  "enabled": true,
  "driver": "com.mysql.jdbc.Driver",
  "url": "jdbc:mysql://localhost:3306/test",
  "username": "root",
  "password": "root"
}
```

MongoDB示例：
```
{
  "type": "mongo",
  "connection": "mongodb://root:root@localhost:27017/data_api_ods?authSource=admin",
  "enabled": true
}
```

##### 6. 验证数据源：在drill-embedded.bat打开的命令行窗口中进行验证

示例：

```
show tables in mysql.test;

show tables in mongo.test;
```

#### 二、Soda配置

##### 1. 软件包安装：pip install -r requirements.txt

##### 2. configuration.yml

根据实际情况修改connection中的host和port

##### 3. main.py数据源配置

在SOURCES中指定Drill的IP和端口，以及需要用到的数据源中的数据库

##### 4. 添加校验规则

checks目录下使用yml文件定义各类校验规则

tips：Soda原生只支持校验，当yml的注释中show_on_fail后面的原生规则校验失败时，自定义的展示内容由python实现

#### 三、本项目用到的Soda原生规则关键字

row_count > 0：行数大于0，用于验证表非空，可选filter参数，先条件筛选后验证行数
row_count same as table：两个表中行数一致
failed rows：当"fail query"中的sql条件或"fail condition"中的条件满足时校验结果为失败
duplicate_count(column) = 0：字段唯一
missing_count(column) = 0：字段非空
missing_percent(column) < 0：字段不全为空，至少一条数据不为空
