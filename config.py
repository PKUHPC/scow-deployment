# encoding: utf-8

# 整个系统的入口端口
PORT = 80

# 镜像信息
# 如果在构建时修改了镜像名和TAG请在这里对应修改
# 如果在构建时没有修改则忽略
IMAGE_BASE = "ghcr.io/pkuhpc/scow"
IMAGE_TAG = "master"

# 整个系统的部署根路径。以/开头，不要以/结尾，如果是根路径写空格
BASE_PATH = ""

# 门户系统部署根路径和镜像后缀。
# 如果是根路径，写空字符串；如果不是根路径，以/开头，不要以/结尾
# 即如果BASE_PATH为/root1，PORTAL_BASE_PATH为root2，那么最终访问portal的路径是/root1/root2
# 下面管理系统相同
# 如果不部署请将PORTAL_DEPLOYED设置为False
PORTAL_DEPLOYED = True
PORTAL_BASE_PATH = ""
PORTAL_IMAGE_POSTFIX = "root"

# 管理系统部署根路径和镜像后缀
# 如果不部署请将MIS_DEPLOYED设置为False
MIS_DEPLOYED = True
MIS_BASE_PATH = "/mis"
MIS_IMAGE_POSTFIX = "mis"

# 管理系统数据库密码。如不部署可以忽略
MIS_DB_PASSWORD = "must!chang3this"

# 是否使用fluentd收集日志
FLUENTD_DEPLOYED = True
# fluentd收集日志的目录
LOG_DIR = "/var/log/fluentd"

