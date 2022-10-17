# SCOW 简易部署

https://pkuhpc.github.io/SCOW/docs/common/deployment

## 生成 Docker compose 文件、compose.sh文件和 db.sh 文件

```shell
# 1. 复制配置文件
cp config-example.py config.py

# 2，根据需求修改config.py

# 3. 生成文件，每次修改了config.py都需要重新运行generate.py脚本以生成对应的docker-compose文件
python generate.py
```

## 部署与卸载

```shell
# 部署
sh compose.sh up -d

# 卸载
sh compose.sh down
```

## 日志收集说明

前提是开启了日志收集功能。各服务日志收集在配置的参数`FLUENTD.LOG_DIR`目录下：

```shell
# 进入日志收集目录
cd {FLUENTD.LOG_DIR}

# 各服务日志存放在该服务名对应的文件夹下
tree -L 1
.
├── auth		 
├── db
├── gateway
├── mis_service
├── mis_web
├── portal-web
└── redis

# 服务日志按日期分割，日志文件命名规则为：{service_name}.yyyymmdd.log
# 例如portal-web日志：
cd portal-web/
ll
-rw-r-----. 1 100 65533 3.1K Oct 12 17:03 portal-web.20221012.log
-rw-r-----. 1 100 65533  27K Oct 13 19:03 portal-web.20221013.log
-rw-r-----. 1 100 65533 113K Oct 14 15:50 portal-web.20221014.log
-rw-r-----. 1 100 65533  83K Oct 15 18:39 portal-web.20221015.log
```



## 连接至管理系统数据库

当部署好了管理系统后，可以在仓库下运行`./db.sh`连接并进入数据库。
