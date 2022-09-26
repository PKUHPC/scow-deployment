# encoding: utf-8

import json

import config

import os


class Compose:
    def __init__(self, services, volumes):
        self.version = "3"
        self.services = services
        self.volumes = volumes


def configItemIsNotNul(configStr):
    if configStr.isspace():
        return False
    else:
        return True


def generate_log_driver(serviceName):
    log_driver = dict()
    log_driver['driver'] = "fluentd"
    opt = dict()
    opt['fluentd-address'] = "localhost:24224"
    opt['mode'] = "non-blocking"
    opt['tag'] = serviceName
    log_driver['options'] = opt
    return log_driver


def generate_log_service():
    log = dict()

    image = "fluentd:v1.14.0-1.0"
    log['image'] = image

    log['restart'] = "unless-stopped"

    ports = ["24224:24224", "24224:24224/udp"]
    log['ports'] = ports

    log_dir = config.LOG_DIR
    os.system('mkdir -p ' + log_dir)
    os.system('chmod +777 ' + log_dir)

    volumes = [log_dir + ":/fluentd/log", "./fluent.conf:/fluentd/etc/fluent.conf"]
    log['volumes'] = volumes

    return log


def generate_gateway_service():
    gateway = dict()

    image = config.IMAGE_BASE + "/gateway:" + config.IMAGE_TAG
    gateway['image'] = image

    gateway['restart'] = "unless-stopped"

    ports = [str(config.PORT) + ":80"]
    gateway['ports'] = ports

    portal_base_path = "/"
    # config.PORTAL_BASE_PATH 未定义
    try:
        if configItemIsNotNul(config.PORTAL_BASE_PATH):
            portal_base_path = config.PORTAL_BASE_PATH
    except AttributeError as e:
        print(e.args)

    mis_base_path = "/mis"
    try:
        if configItemIsNotNul(config.MIS_BASE_PATH):
            mis_base_path = config.MIS_BASE_PATH
    except AttributeError as e:
        print(e.args)

    environment = ["BASE_PATH=" + config.BASE_PATH, "PORTAL_PATH=" + portal_base_path, "MIS_PATH=" + mis_base_path]
    gateway['environment'] = environment

    if config.FLUENTD_DEPLOYED:
        gateway["logging"] = generate_log_driver("gateway")
        gateway["depends_on"] = ["log"]
    return gateway


def generate_auth_service():
    auth = dict()

    image = config.IMAGE_BASE + "/auth:" + config.IMAGE_TAG
    auth['image'] = image

    auth['restart'] = "unless-stopped"

    volumes = ["/etc/hosts:/etc/hosts", "./config:/etc/scow"]
    auth['volumes'] = volumes

    environment = ["BASE_PATH=" + config.BASE_PATH]
    auth['environment'] = environment

    if config.FLUENTD_DEPLOYED:
        auth["logging"] = generate_log_driver("auth")
        auth["depends_on"] = ["log"]
    return auth


def generate_redis_service():
    redis = dict()

    image = "redis:alpine"
    redis['image'] = image

    redis['restart'] = "unless-stopped"

    if config.FLUENTD_DEPLOYED:
        redis["logging"] = generate_log_driver("redis")
        redis["depends_on"] = ["log"]
    return redis


def generate_portal_web_service():
    portal_web = dict()

    portal_image_postfix = "root"
    if configItemIsNotNul(config.PORTAL_IMAGE_POSTFIX):
        portal_image_postfix = config.PORTAL_IMAGE_POSTFIX
    image = config.IMAGE_BASE + "/portal-web-" + portal_image_postfix + ":" + config.IMAGE_TAG
    portal_web['image'] = image

    portal_web['restart'] = "unless-stopped"

    if config.MIS_DEPLOYED:
        mis_deployed = "true"
    else:
        mis_deployed = "false"

    mis_base_path = "/mis"
    try:
        if configItemIsNotNul(config.MIS_BASE_PATH):
            mis_base_path = config.MIS_BASE_PATH
    except AttributeError as e:
        print(e.args)

    environment = ["BASE_PATH=" + config.BASE_PATH, "MIS_URL=" + mis_base_path, "MIS_DEPLOYED=" + mis_deployed]
    portal_web['environment'] = environment

    volumes = ["/etc/hosts:/etc/hosts", "./config:/etc/scow", "~/.ssh:/root/.ssh"]
    portal_web['volumes'] = volumes

    if config.FLUENTD_DEPLOYED:
        portal_web["logging"] = generate_log_driver("portal-web")
        portal_web["depends_on"] = ["log"]
    return portal_web


def generate_db_service():
    mysqldb = dict()

    image = "mysql:8"
    mysqldb['image'] = image

    mysqldb['restart'] = "unless-stopped"

    volumes = ["db_data:/var/lib/mysql"]
    mysqldb['volumes'] = volumes

    environment = ["MYSQL_ROOT_PASSWORD=" + config.MIS_DB_PASSWORD]
    mysqldb['environment'] = environment

    if config.FLUENTD_DEPLOYED:
        mysqldb["logging"] = generate_log_driver("db")
        mysqldb["depends_on"] = ["log"]
    return mysqldb


def generate_mis_service():
    mis_service = dict()

    image = config.IMAGE_BASE + "/mis-server:" + config.IMAGE_TAG
    mis_service['image'] = image

    mis_service['restart'] = "unless-stopped"

    environment = ["DB_PASSWORD=" + config.MIS_DB_PASSWORD]
    mis_service['environment'] = environment

    volumes = ["/etc/hosts:/etc/hosts", "./config:/etc/scow", "/root/.ssh:/root/.ssh"]
    mis_service['volumes'] = volumes

    if config.FLUENTD_DEPLOYED:
        mis_service["logging"] = generate_log_driver("mis_service")
        mis_service["depends_on"] = ["log"]
    return mis_service


def generate_mis_web_service():
    mis_web = dict()

    mis_image_postfix = "root"
    if configItemIsNotNul(config.MIS_IMAGE_POSTFIX):
        mis_image_postfix = config.MIS_IMAGE_POSTFIX
    image = config.IMAGE_BASE + "/mis-web-" + mis_image_postfix + ":" + config.IMAGE_TAG
    mis_web['image'] = image

    mis_web['restart'] = "unless-stopped"

    if config.PORTAL_DEPLOYED:
        portal_deployed = "true"
    else:
        portal_deployed = "false"

    portal_base_path = "/"
    try:
        if configItemIsNotNul(config.PORTAL_BASE_PATH):
            portal_base_path = config.PORTAL_BASE_PATH
    except AttributeError as e:
        print(e.args)

    environment = ["BASE_PATH=" + config.BASE_PATH, "PORTAL_URL=" + portal_base_path,
                   "PORTAL_DEPLOYED=" + portal_deployed]
    mis_web['environment'] = environment

    volumes = ["./config:/etc/scow"]
    mis_web['volumes'] = volumes

    if config.FLUENTD_DEPLOYED:
        mis_web["logging"] = generate_log_driver("mis_web")
        mis_web["depends_on"] = ["log"]
    return mis_web


def generate_service():
    service = dict()

    if config.FLUENTD_DEPLOYED:
        lg = generate_log_service()
        service["log"] = lg

    gw = generate_gateway_service()
    au = generate_auth_service()
    rs = generate_redis_service()
    service["gateway"] = gw
    service["auth"] = au
    service["redis"] = rs

    if config.PORTAL_DEPLOYED:
        pw = generate_portal_web_service()
        service["portal-web"] = pw

    if config.MIS_DEPLOYED:
        db = generate_db_service()
        ms = generate_mis_service()
        mw = generate_mis_web_service()
        service["db"] = db
        service["mis-server"] = ms
        service["mis-web"] = mw

    return service


if __name__ == '__main__':
    svc = generate_service()

    data = dict()
    # data = {"db_data": None}
    data["db_data"] = dict()
    com = Compose(svc, data)
    com_json = json.dumps(com.__dict__)
    str_json = json.loads(com_json)

    with open("docker-compose.json", "w") as json_file:
        json.dump(str_json, json_file, indent=4, ensure_ascii=False)

    print("Docker compose file generated successfully! ")
