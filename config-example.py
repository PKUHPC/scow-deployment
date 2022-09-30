# encoding: utf-8

# ------- 全局通用配置 -------
#
# COMMON.PORT: 整个系统的入口端口
# COMMON.BASE_PATH: 整个系统的部署根路径。以/开头，不要以/结尾，如果是根路径写"/"
# COMMON.IMAGE_BASE: 镜像仓库地址，据实际情况填写
# COMMON.IMAGE_TAG: 镜像tag，据实际情况填写
COMMON = {
  "PORT": 80,
  "BASE_PATH": "/",
  "IMAGE_BASE": "ghcr.io/pkuhpc/scow",
  "IMAGE_TAG": "master",
}

#
# ------- 门户系统 -------
#
# PORTAL.BASE_PATH: 以/开头，不要以/结尾. 如果BASE_PATH为/root1，PORTAL.BASE_PATH为root2，那么最终访问门户系统的路径是/root1/root2
# PORTAL.IMAGE_POSTFIX: 门户系统镜像后缀
PORTAL = {
  "BASE_PATH": "/",
  "IMAGE_POSTFIX": "root"
}
# 若不部署门户系统，设置PORTAL = False
# PORTAL = False

#
# ------- 管理系统 -------
#
# MIS.BASE_PATH: 以/开头，不要以/结尾. 如果BASE_PATH为/root1，MIS.BASE_PATH为root2，那么最终访问管理系统的路径是/root1/root2
# MIS.IMAGE_POSTFIX: 管理系统镜像后缀
MIS = {
  "BASE_PATH": "/mis",
  "IMAGE_POSTFIX": "mis",
  "DB_PASSWORD": "must!chang3this"
}
# 若不部署管理系统，设置MIS = False
# MIS = False

#
# ------- 日志收集服务 -------
#
# FLUENTD.LOG_DIR：收集日志的目录，不存在会自动创建
FLUENTD = {
  "LOG_DIR": "/var/log/fluentd",
}
# 若不部署日志收集服务，FLUENTD = False
# FLUENTD = False

