import sys
import os
import json

CONFIG_PATH = "config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError("config.json not found")
    with open(CONFIG_PATH) as f:
        return json.load(f)

def generate_dockerfile(dbms=None, version=None):
    config = load_config()
    dbms = dbms or config.get("dbms")
    version = version or config.get("version")
    dbms_dir = os.path.join(dbms)
    init_sql_path = os.path.join(dbms_dir, "init.sql")

    dockerfile = f"""FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \\
    apt-get install -y default-jdk maven git jq curl unzip python3 python3-pip && \\
    rm -rf /var/lib/apt/lists/*

"""

    install_script = ""
    if dbms == "mysql":
        from mysql.docker_ops import get_install_script
        install_script = get_install_script(version)
    elif dbms == "postgres":
        from postgres.docker_ops import get_install_script
        install_script = get_install_script(version)
    else:
        raise ValueError(f"Unsupported DBMS: {dbms}")

    dockerfile += install_script


    dockerfile += f"""
COPY entrypoint.sh /root/entrypoint.sh
COPY config.json /root/config.json
COPY {dbms} /root/{dbms}
WORKDIR /root
RUN mkdir -p /root/sqlancer && chmod +x /root/entrypoint.sh
"""

    if os.path.exists(init_sql_path):
        dockerfile += f"""
COPY {init_sql_path} /db_init/init.sql
RUN chmod 755 /db_init && chmod 644 /db_init/init.sql
"""

    dockerfile += 'CMD ["/root/entrypoint.sh"]\n'

    with open("Dockerfile", "w") as f:
        f.write(dockerfile)

    print(f"✅ Dockerfile generated，including {dbms}:{version} ")

if __name__ == "__main__":
    dbms_arg = sys.argv[1] if len(sys.argv) > 1 else None
    version_arg = sys.argv[2] if len(sys.argv) > 2 else None
    generate_dockerfile(dbms_arg, version_arg)
