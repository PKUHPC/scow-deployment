# SCOW简易部署

https://pkuhpc.github.io/SCOW/docs/common/deployment


## 生成 Docker compose文件
```shell
python main.py
```
## 部署与卸载
```shell
# 部署
docker-compose -f docker-compose.json up -d

# 卸载
docker-compose -f docker-compose.json down
```
## 参数说明
自定义参数详见config.py

|       参数名称       |                          参数说明                          |
| :------------------: | :--------------------------------------------------------: |
|         PORT         |                     整个系统的入口端口                     |
|      IMAGE_BASE      |                        镜像仓库地址                        |
|      IMAGE_TAG       |                          镜像tag                           |
|      BASE_PATH       |                    整个系统的部署根路径                    |
|   PORTAL_DEPLOYED    |      门户系统部署开关：True表示部署，False表示不部署       |
|   PORTAL_BASE_PATH   |                        门户访问路径                        |
| PORTAL_IMAGE_POSTFIX |                      门户系统镜像后缀                      |
|     MIS_DEPLOYED     |      管理系统部署开关：True表示部署，False表示不部署       |
|    MIS_BASE_PATH     |                      管理系统访问路径                      |
| PORTAL_IMAGE_POSTFIX |                      管理系统镜像后缀                      |
|   MIS_DB_PASSWORD    |                     管理系统数据库密码                     |
|   FLUENTD_DEPLOYED   | fluentd日志收集服务部署开关：True表示部署，False表示不部署 |
|       LOG_DIR        |                   fluentd收集日志的目录                    |

## 连接至管理系统数据库

当部署好了管理系统后，可以在仓库下运行`./db.sh`连接并进入数据库。