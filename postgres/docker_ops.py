# postgres/docker_ops.py

import subprocess
import os


def get_install_script(version: str) -> str:
    """
    return postgresql dockerfile
    """
    return f"""
# install PostgreSQL {version}
RUN apt-get update && \\
    apt-get install -y postgresql postgresql-contrib && \\
    rm -rf /var/lib/apt/lists/*
"""

def pull_docker_image(version: str):
    """
    pull PostgreSQL 
    """
    image = f"postgres:{version}"
    print(f"[PostgreSQL] pull {image} ...")
    subprocess.run(["sudo", "docker", "pull", image], check=True)

def init(sql_password: str):
    print("[POSTGRES] Starting PostgreSQL...")
    subprocess.run("service postgresql start", shell=True, check=True)
    init_sql = "/db_init/init.sql"
    if os.path.exists(init_sql):
        print("[POSTGRES] Executing init.sql...")
        
        subprocess.run(f"su - postgres -c \"psql < {init_sql}\"", shell=True, check=True)
