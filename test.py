import os
import sys
import json
import subprocess
import time
import shlex
from datetime import datetime
from utils import run_command

def container_exists(name):
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    return name in result.stdout.strip().splitlines()

def start_db_container(dbms, cfg, script_log, docker_log):
    image = cfg.get("image")
    container_name = cfg.get("container_name", f"{dbms}-sqlancer")
    env_dict = cfg.get("env", {})

    if not image:
        script_log.error( "Missing 'image' field in config.json")
        sys.exit(1)

    if container_exists(container_name):
        script_log.info( "Container already exists, remove the old container and restart")
        remove_container(container_name, script_log, docker_log)

    env_vars = []
    for k, v in env_dict.items():
        env_vars += ["-e", f"{k}={v}"]

    run_command([
        "docker", "run", "-d",
        "--name", container_name,
        "--network", "sqlancer-net",
        *env_vars,
        image
    ], docker_log)

    script_log.info("Starting DBMS container...")
    time.sleep(10)

    
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
            script_log.info("Running init SQL inside container...")
            run_command(full_cmd, docker_log)
        except Exception as e:
            script_log.warning("Init SQL failed")

    script_log.info("DBMS container started")

def start_sqlancer_container(dbms, host_container_name, username, password, oracle, threads, timeout, script_log, docker_log, sqlancer_log, run_dir):
    script_log.info("Executing test...")
    # date = datetime.today().strftime("%y-%m-%d-%H-%M-%S")  
    # log_dir_host = os.path.abspath(os.path.join("logs", date))
    # os.makedirs(log_dir_host, exist_ok=True)

    log_dir_host = os.path.abspath(run_dir)
    os.makedirs(log_dir_host, exist_ok=True)

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
        # "-v", f"{log_dir_host}:/logs",
        "-v", f"{log_dir_host}:/root/sqlancer/target/logs",
        "sqlancer:latest"
    ], sqlancer_log)
    script_log.info("Test executed")


def test_single(cfg, script_log, docker_log, sqlancer_log, run_dir, use_cache=False):
    script_log.info("==============================Executing test==============================")
    if cfg["embedded"] == "no":
        start_db_container(cfg["dbms"], cfg, script_log, docker_log)

    start_sqlancer_container(
        dbms=cfg["dbms"],
        host_container_name=cfg["container_name"],
        username=cfg["username"],
        password=cfg["password"],
        oracle=cfg["oracle"],
        threads=cfg["num_threads"],
        timeout=cfg["timeout_seconds"],
        script_log=script_log,
        sqlancer_log=sqlancer_log,
        docker_log=docker_log,
        run_dir=run_dir
    )

    if cfg["embedded"] == "no":
        remove_container(cfg["container_name"], script_log, docker_log)
    script_log.info("==============================Executing test==============================")

def remove_container(container_name, script_log, docker_log):
    script_log.info("Removing container...")
    try:
        run_command(["docker", "rm", "-f", container_name], docker_log)
        script_log.info("Container removed")
    except subprocess.CalledProcessError as e:
        script_log.warning("Container removing failed")


def test_custom_dockerfile(dockerfile_path, cfg, script_log, docker_log, sqlancer_log, run_dir, use_cache=False):
    script_log.info("==============================Executing test==============================")
    
    dbms=cfg["dbms"]

    start_db_container(dbms, cfg, script_log, docker_log)
    start_sqlancer_container(
        dbms=dbms,
        host_container_name=cfg["container_name"],
        username=cfg["username"],
        password=cfg["password"],
        oracle=cfg["oracle"],
        threads=cfg["num_threads"],
        timeout=cfg["timeout_seconds"],
        script_log=script_log,
        sqlancer_log=sqlancer_log,
        docker_log=docker_log,
        run_dir=run_dir
    )

    remove_container(cfg["container_name"], script_log, docker_log)
    script_log.info("==============================Executing test==============================")

