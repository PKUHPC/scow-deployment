# encoding: utf-8

import json
import os
import stat
import config as cfg
import subprocess


class Service:
    def __init__(self, name, image, ports, volumes, environment):
        self.name = name
        self.image = image
        self.restart = "unless-stopped"
        self.ports = tuple_to_array(ports)
        self.volumes = dict_to_array(volumes)
        self.environment = dict_to_array(environment, True)
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


FLUENTD_IMAGE_TAG = "v1.14.0-1.0"
REDIS_IMAGE_TAG = "alpine"
MYSQL_IMAGE_TAG = "8"


def tuple_to_array(t):
    if t is None:
        return None
    arr = []
    for term in t:
        arr.append(term[0] + ":" + term[1])
    return arr


def dict_to_array(dict_data, *parameter):
    if dict_data is None:
        return None
    arr = []
    is_env = parameter[0] if len(parameter) > 0 else False
    for key in dict_data:
        if is_env:
            arr.append(key + "=" + dict_data[key])
        else:
            arr.append(key + ":" + dict_data[key])
    return arr


def generate_image(name, postfix):
    if postfix is None:
        return cfg.COMMON["IMAGE_BASE"] + "/" + name + ":" + cfg.COMMON["IMAGE_TAG"]
    else:
        return cfg.COMMON["IMAGE_BASE"] + "/" + name + "-" + postfix + ":" + cfg.COMMON["IMAGE_TAG"]


def generate_path_common(property_data, is_common):
    if property_data:
        if property_data["BASE_PATH"] != "/" and (
                property_data["BASE_PATH"].isspace() or property_data["BASE_PATH"].endswith("/") or not property_data["BASE_PATH"].startswith("/")):
            raise Exception("path should start with '/' and cannot end with '/' or be empty ")
        else:
            ret = "" if is_common else "/"
            return ret if property_data["BASE_PATH"] == "/" else property_data["BASE_PATH"]
    else:
        return ""


def generate_path(property_data, system_module):
    if property_data:
        if "BASE_PATH" not in property_data.keys():
            if system_module == "MIS":
                return "/mis"
            elif system_module == "PORTAL":
                if cfg.COMMON["BASE_PATH"] != "/":
                    return ""
                else:
                    return "/"
            else:
                raise Exception("parameter error")
        if cfg.COMMON["BASE_PATH"] != "/":
            return generate_path_common(property_data, True)
        else:
            return generate_path_common(property_data, False)
    else:
        return ""


def create_log_service():
    # 创建日志收集目录 mkdir -p ***
    if os.path.exists(cfg.FLUENTD["LOG_DIR"]):
        print("log dir already exists!")
    else:
        os.makedirs(cfg.FLUENTD["LOG_DIR"])
        print("log dir created successfully!")

    os.chmod(cfg.FLUENTD["LOG_DIR"], stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    log_ports = [("24224", "24224"), ("24224", "24224/udp")]
    log_volumes = {
        cfg.FLUENTD["LOG_DIR"]: "/fluentd/log",
        "./fluent/fluent.conf": "/fluentd/etc/fluent.conf"
    }
    log = Service("log", "fluentd:" + FLUENTD_IMAGE_TAG, log_ports, log_volumes, None)
    return log


def create_gateway_service():
    gw_ports = [("80", "80")]
    gw_env = {
        "BASE_PATH": generate_path_common(cfg.COMMON, True),
        "PORTAL_PATH": generate_path(cfg.PORTAL, "PORTAL"),
        "MIS_PATH": generate_path(cfg.MIS, "MIS")
    }
    gateway = Service("gateway", generate_image("gateway", None), gw_ports, None, gw_env)
    return gateway


def create_auth_service():
    au_env = {
        "BASE_PATH": generate_path_common(cfg.COMMON, True)
    }
    au_volumes = {
        "/etc/hosts": "/etc/hosts",
        "./config": "/etc/scow"
    }
    auth = Service("auth", generate_image("auth", None), None, au_volumes, au_env)
    return auth


def create_portal_web_service():
    pw_env = {
        "BASE_PATH": generate_path_common(cfg.COMMON, True),
        "MIS_URL": generate_path(cfg.MIS, "MIS"),
        "MIS_DEPLOYED": "true" if cfg.MIS else "false"
    }
    pw_volumes = {
        "/etc/hosts": "/etc/hosts",
        "./config": "/etc/scow",
        "~/.ssh": "/root/.ssh"
    }
    portal_web = Service("portal-web", generate_image("portal-web", cfg.PORTAL["IMAGE_POSTFIX"]), None,
                         pw_volumes, pw_env)
    return portal_web


def create_db_service():
    db_volumes = {
        "db_data": "/var/lib/mysql"
    }
    db_env = {
        "MYSQL_ROOT_PASSWORD": cfg.MIS["DB_PASSWORD"]
    }
    db = Service("db", "mysql:" + MYSQL_IMAGE_TAG, None, db_volumes, db_env)
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
    mis_server = Service("mis-server", generate_image("mis-server", None), None, ms_volumes, ms_env)
    return mis_server


def create_mis_web_service():
    mv_env = {
        "BASE_PATH": generate_path_common(cfg.COMMON, True),
        "PORTAL_URL": generate_path(cfg.PORTAL, "PORTAL"),
        "PORTAL_DEPLOYED": "true" if cfg.PORTAL else "false"
    }
    mv_volumes = {
        "./config": "/etc/scow",
    }
    mis_web = Service("mis-web", generate_image("mis-web", cfg.MIS["IMAGE_POSTFIX"]), None, mv_volumes, mv_env)
    return mis_web


def create_services():
    com = Compose()

    if cfg.FLUENTD:
        com.add_service(create_log_service())

    com.add_service(create_gateway_service())
    com.add_service(create_auth_service())
    com.add_service(Service("redis", "redis:" + REDIS_IMAGE_TAG, None, None, None))

    if cfg.PORTAL:
        com.add_service(create_portal_web_service())

    if cfg.MIS:
        com.add_service(create_db_service())
        com.add_service(create_mis_server_service())
        com.add_service(create_mis_web_service())

    return com


def cmd_is_exist(cmd):
    try:
        subprocess.check_output(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def chmod_shell_script(script_name):
    os.chmod(script_name, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


def create_files():
    files = "docker-compose.json, compose.sh "
    cmd_str = ""
    with open("compose.sh", "w") as file:
        if cmd_is_exist("docker compose"):
            cmd_str = "docker compose"
        elif cmd_is_exist("docker-compose"):
            cmd_str = "docker-compose"
        else:
            raise Exception("Docker Compose is not installed, refer to this connection for installation: "
                            "https://docs.docker.com/compose/install/linux/#install-the-plugin-manually")

        file.write(cmd_str + " -f docker-compose.json $@")
        chmod_shell_script("compose.sh")

    if cfg.MIS:
        files = files + " and db.sh generated successfully!"
        # 生成 db.sh文件
        with open("db.sh", "w") as file:
            db_passwd = cfg.MIS["DB_PASSWORD"]
            file.write(cmd_str + " -f docker-compose.json exec db mysql -uroot -p'" + db_passwd + "'")
            chmod_shell_script("db.sh")
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
