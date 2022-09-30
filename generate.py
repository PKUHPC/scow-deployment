# encoding: utf-8

import json
import os
import stat

import config
import config as cfg


class Service:
    def __init__(self, name, image, ports, volumes, environment):
        self.name = name
        self.image = image
        self.restart = "unless-stopped"
        self.ports = ports
        self.volumes = volumes
        self.environment = environment
        self.logging = None
        self.depends_on = ["log"]
        if cfg.FLUENTD and self.name != "log":
            self.add_logging()
        else:
            self.depends_on = None

    def add_logging(self):
        self.logging = {
            "driver": "fluentd",
            "options": {
                "fluentd-address": "localhost:24224",
                "mode": "non-blocking",
                "tag": self.name
            }
        }


class Compose:
    def __init__(self):
        self.version = "3"
        self.services = {}
        self.volumes = {
            "db_data": {}
        }

    def add_service(self, sv):
        sv_dict = sv.__dict__
        element = sv_dict.pop("name")
        self.services[element] = clear_dict(sv_dict)


def clear_dict(d):
    if d is None:
        return None
    elif isinstance(d, list):
        return list(filter(lambda x: x is not None, map(clear_dict, d)))
    elif not isinstance(d, dict):
        return d
    else:
        r = dict(
            filter(lambda x: x[1] is not None,
                   map(lambda x: (x[0], clear_dict(x[1])),
                       d.items())))
        if not bool(r):
            return None
        return r


def tuple_to_array(t):
    arr = []
    for term in t:
        arr.append(term[0] + ":" + term[1])
    return arr


def dict_to_array(d):
    arr = []
    for key in d:
        arr.append(key + ":" + d[key])
    return arr


def generate_image(name, postfix):
    if postfix is None:
        return cfg.COMMON["IMAGE_BASE"] + "/" + name + ":" + cfg.COMMON["IMAGE_TAG"]
    else:
        return cfg.COMMON["IMAGE_BASE"] + "/" + name + "-" + postfix + ":" + cfg.COMMON["IMAGE_TAG"]


def generate_path(p):
    if p:
        return "" if p["BASE_PATH"] == "/" else p["BASE_PATH"]
    else:
        return ""


def create_log_service():
    # 创建日志收集目录 mkdir -p ***
    try:
        os.makedirs(cfg.FLUENTD["LOG_DIR"], stat.S_IRWXO)
        print("log dir created successfully!")
    except OSError:
        print("log dir already exists!")

    os.chmod(cfg.FLUENTD["LOG_DIR"], stat.S_IRWXO)

    log_ports = [("24224", "24224"), ("24224", "24224/udp")]
    log_volumes = {
        cfg.FLUENTD["LOG_DIR"]: "/fluentd/log",
        "./fluent/fluent.conf": "/fluentd/etc/fluent.conf"
    }
    log = Service("log", "fluentd:v1.14.0-1.0", tuple_to_array(log_ports), dict_to_array(log_volumes), None)
    return log


def create_gateway_service():
    gw_ports = [("80", "80")]
    gw_env = {
        "BASE_PATH": generate_path(cfg.COMMON),
        "PORTAL_PATH": generate_path(cfg.PORTAL),
        "MIS_PATH": generate_path(cfg.MIS)
    }
    gateway = Service("gateway", generate_image("gateway", None), tuple_to_array(gw_ports), None, dict_to_array(gw_env))
    return gateway


def create_auth_service():
    au_env = {
        "BASE_PATH": generate_path(cfg.COMMON)
    }
    au_volumes = {
        "/etc/hosts": "/etc/hosts",
        "./config": "/etc/scow"
    }
    auth = Service("auth", generate_image("auth", None), None, dict_to_array(au_volumes), dict_to_array(au_env))
    return auth


def create_portal_web_service():
    pw_env = {
        "BASE_PATH": generate_path(cfg.COMMON),
        "MIS_URL": generate_path(cfg.MIS),
        "MIS_DEPLOYED": "true" if cfg.MIS else "false"
    }
    pw_volumes = {
        "/etc/hosts": "/etc/hosts",
        "./config": "/etc/scow",
        "~/.ssh": "/root/.ssh"
    }
    portal_web = Service("portal-web", generate_image("portal-web", cfg.PORTAL["IMAGE_POSTFIX"]), None,
                         dict_to_array(pw_volumes), dict_to_array(pw_env))
    return portal_web


def create_db_service():
    db_volumes = {
        "db_data": "/var/lib/mysql"
    }
    db_env = {
        "MYSQL_ROOT_PASSWORD": cfg.MIS["DB_PASSWORD"]
    }
    db = Service("db", "mysql:8", None, dict_to_array(db_volumes), dict_to_array(db_env))
    return db


def create_mis_server_service():
    ms_env = {
        "DB_PASSWORD": cfg.MIS["DB_PASSWORD"]
    }
    ms_volumes = {
        "/etc/hosts": "/etc/hosts",
        "./config": "/etc/scow",
        "~/.ssh": "/root/.ssh"
    }
    mis_server = Service("mis-server", generate_image("mis-server", None), None, dict_to_array(ms_volumes),
                         dict_to_array(ms_env))
    return mis_server


def create_mis_web_service():
    mv_env = {
        "BASE_PATH": generate_path(cfg.COMMON),
        "PORTAL_URL": generate_path(cfg.PORTAL),
        "PORTAL_DEPLOYED": "true" if cfg.PORTAL else "false"
    }
    mv_volumes = {
        "./config": "/etc/scow",
    }
    mis_web = Service("mis-web", generate_image("mis-web", cfg.MIS["IMAGE_POSTFIX"]), None, dict_to_array(mv_volumes),
                      dict_to_array(mv_env))
    return mis_web


def create_services():
    com = Compose()

    if cfg.FLUENTD:
        com.add_service(create_log_service())

    com.add_service(create_gateway_service())
    com.add_service(create_auth_service())
    com.add_service(Service("redis", "redis:alpine", None, None, None))

    if cfg.PORTAL:
        com.add_service(create_portal_web_service())

    if cfg.MIS:
        com.add_service(create_db_service())
        com.add_service(create_mis_server_service())
        com.add_service(create_mis_web_service())

    return com


def create_files():
    files = "docker-compose.json"
    if cfg.MIS:
        files = files + " and db.sh generated successfully!"
        # 生成 db.sh文件
        with open("db.sh", "w") as file:
            db_passwd = config.MIS["DB_PASSWORD"]
            file.write("docker-compose -f docker-compose.json exec db mysql -uroot -p'" + db_passwd + "'")
            os.chmod("db.sh", stat.S_IRWXO)
    else:
        files = files + " generated successfully!"

    dc = create_services()
    com_json = json.dumps(dc.__dict__, skipkeys=True)
    str_json = json.loads(com_json)
    # 生成compose文件
    with open("docker-compose.json", "w") as json_file:
        json.dump(str_json, json_file, indent=4, ensure_ascii=False)
    return files


if __name__ == "__main__":
    print_info = create_files()
    print(print_info)
