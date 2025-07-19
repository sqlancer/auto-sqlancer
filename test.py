import os
import sys
import json
import subprocess
import time
import shlex
from datetime import datetime

def run_command(cmd, **kwargs):
    print("[CMD]", " ".join(cmd))
    subprocess.run(cmd, check=True, **kwargs)

def container_exists(name):
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    return name in result.stdout.strip().splitlines()

def start_db_container(dbms, cfg):
    image = cfg.get("image")
    container_name = cfg.get("container_name", f"{dbms}-sqlancer")
    env_dict = cfg.get("env", {})

    if not image:
        print("[ERROR] Missing 'image' field in config.json")
        sys.exit(1)

    if container_exists(container_name):
        print(f"[INFO] Container '{container_name}' already exists. Remove the old container and restart.")
        remove_container(container_name)

    env_vars = []
    for k, v in env_dict.items():
        env_vars += ["-e", f"{k}={v}"]

    run_command([
        "docker", "run", "-d",
        "--name", container_name,
        "--network", "sqlancer-net",
        *env_vars,
        image
    ])


    print(f"[INFO] Waiting for DBMS container '{container_name}' to be ready...")
    time.sleep(10)

    # Optional init SQL
    init_sql = cfg.get("init_sql")
    init_cmd_template = cfg.get("init_sql_command_template")
    if init_sql and init_cmd_template:
        try:
            cmd_str = init_cmd_template.format(
                username=cfg["username"],
                password=cfg.get("password", ""),
                sql=init_sql
            )
            full_cmd = ["docker", "exec", container_name] + shlex.split(cmd_str)
            print(f"[INFO] Running init SQL inside container: {init_sql}")
            run_command(full_cmd)
        except Exception as e:
            print(f"[WARNING] Failed to run init SQL: {e}")

def start_sqlancer_container(dbms, host_container_name, username, password, oracle, threads, timeout):
    date = datetime.today().strftime("%y-%m-%d-%H-%M-%S")  
    log_dir_host = os.path.abspath(os.path.join("logs", date))
    os.makedirs(log_dir_host, exist_ok=True)

    run_log_container_dir = "/logs"
    sqlancer_logs_container_dir = "/root/sqlancer/target/logs"

    run_command([
        "docker", "run", "--rm",
        "--name", "auto-sqlancer",
        "--network", "sqlancer-net",
        "-e", f"SQLANCER_DBMS={dbms}",
        "-e", f"SQLANCER_HOST={host_container_name}",
        "-e", f"SQLANCER_USERNAME={username}",
        "-e", f"SQLANCER_PASSWORD={password}",
        "-e", f"SQLANCER_ORACLE={oracle}",
        "-e", f"SQLANCER_THREADS={threads}",
        "-e", f"SQLANCER_TIMEOUT={timeout}",
        "-v", f"{log_dir_host}:{run_log_container_dir}",
        "-v", f"{log_dir_host}:{sqlancer_logs_container_dir}",
        "sqlancer:latest"
    ])


def test_single(dbms, cfg, use_cache=False):

    start_db_container(dbms, cfg)
    start_sqlancer_container(
        dbms=dbms,
        host_container_name=cfg["container_name"],
        username=cfg["username"],
        password=cfg["password"],
        oracle=cfg["oracle"],
        threads=cfg["num_threads"],
        timeout=cfg["timeout_seconds"]
    )

    remove_container(cfg["container_name"])

def remove_container(container_name):
    try:
        print(f"[INFO] Removing container: {container_name}")
        subprocess.run(["docker", "rm", "-f", container_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Failed to remove container {container_name}: {e}")




def test_custom_dockerfile(dockerfile_path, cfg, use_cache=False):
    dbms=cfg["dbms"]

    start_db_container(dbms, cfg)
    start_sqlancer_container(
        dbms=dbms,
        host_container_name=cfg["container_name"],
        username=cfg["username"],
        password=cfg["password"],
        oracle=cfg["oracle"],
        threads=cfg["num_threads"],
        timeout=cfg["timeout_seconds"]
    )

    remove_container(cfg["container_name"])


