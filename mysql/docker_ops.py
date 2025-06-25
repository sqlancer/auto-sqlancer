# mysql/docker_ops.py

import subprocess
import os


def get_install_script(version: str) -> str:
    """
    return MySQL - Dockerfile 
    """
    return f"""
# install MySQL {version}
RUN apt-get update && \\
    apt-get install -y mysql-server && \\
    rm -rf /var/lib/apt/lists/*
"""

def pull_docker_image(version: str):
    """
    pull MySQL 
    """
    image = f"mysql:{version}"
    print(f"[MySQL]  {image} ...")
    subprocess.run(["sudo", "docker", "pull", image], check=True)

def init(sql_password: str):
    print("[MYSQL] Starting MySQL...")
    subprocess.run("service mysql start", shell=True, check=True)
    print("[MYSQL] Setting root password...")
    
    subprocess.run(
        f"mysql -u root <<EOF\n"
        f"ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{sql_password}';\n"
        f"FLUSH PRIVILEGES;\n"
        f"EOF", shell=True, check=True
    )
    init_sql = "/db_init/init.sql"
    if os.path.exists(init_sql):
        print("[MYSQL] Executing init.sql...")
        subprocess.run(f"mysql -u root -p'{sql_password}' < {init_sql}", shell=True, check=True)