# SCOW 简易部署

https://pkuhpc.github.io/SCOW/docs/common/deployment

## 生成 Docker compose 文件和 db.sh 文件

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
docker-compose -f docker-compose.json up -d

# 卸载
docker-compose -f docker-compose.json down
```

## 参数说明

自定义参数说明详见 config.py

|       参数名称       |                                        参数说明                                         |
| :------------------: | :-------------------------------------------------------------------------------------: |
|     COMMON.PORT      |                                   整个系统的入口端口                                    |
|   COMMON.BASE_PATH   |                                  整个系统的部署根路径                                   |
|  COMMON.IMAGE_BASE   |                                      镜像仓库地址                                       |
|   COMMON.IMAGE_TAG   |                                        镜像 tag                                         |
|        PORTAL        |         门户系统部署开关, False 表示不部署, 若部署需要配置以下 PORTAL.××× 参数          |
|   PORTAL.BASE_PATH   |                                      门户访问路径                                       |
| PORTAL.IMAGE_POSTFIX |                                    门户系统镜像后缀                                     |
|         MIS          |           管理系统部署开关, False 表示不部署, 若部署需要配置以下 MIS.××× 参数           |
|    MIS.BASE_PATH     |                                    管理系统访问路径                                     |
|  MIS.IMAGE_POSTFIX   |                                    管理系统镜像后缀                                     |
|   MIS.DB_PASSWORD    |                                   管理系统数据库密码                                    |
|       FLUENTD        | fluentd 日志收集服务部署开关, False 表示不部署, 若部署需要配置以下 FLUENTD.LOG_DIR 参数 |
|   FLUENTD.LOG_DIR    |                                 fluentd 收集日志的目录                                  |

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
