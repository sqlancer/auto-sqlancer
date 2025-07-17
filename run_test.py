import os
import sys
import json
import subprocess
import time
import shlex
from datetime import datetime

def load_json(path):
    with open(path) as f:
        return json.load(f)

def run_command(cmd, **kwargs):
    print("[CMD]", " ".join(cmd))
    subprocess.run(cmd, check=True, **kwargs)

def ensure_sqlancer_image(force_rebuild=False):
    if force_rebuild:
        print("[INFO] Rebuilding SQLancer image due to --cache not specified...")
        run_command(["docker", "build", "--no-cache", "-t", "sqlancer:latest", "./sqlancer"])
        return

    result = subprocess.run(
        ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
        capture_output=True, text=True
    )
    images = result.stdout.strip().splitlines()
    if "sqlancer:latest" in images:
        print("[INFO] SQLancer image already exists: sqlancer:latest")
    else:
        print("[INFO] SQLancer image not found. Building from ./sqlancer...")
        run_command(["docker", "build", "-t", "sqlancer:latest", "./sqlancer"])


def container_exists(name):
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    return name in result.stdout.strip().splitlines()

def start_db_container(dbms, config_path):
    if not os.path.exists(config_path):
        print(f"[ERROR] config.json not found: {config_path}")
        sys.exit(1)

    cfg = load_json(config_path)
    image = cfg.get("image")
    container_name = cfg.get("container_name", f"{dbms}-sqlancer")
    env_dict = cfg.get("env", {})

    if not image:
        print("[ERROR] Missing 'image' field in config.json")
        sys.exit(1)

    if container_exists(container_name):
        print(f"[INFO] Container '{container_name}' already exists. Skipping startup.")
        return

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

def build_environment(dbms, config_path, use_cache, custom=False, dockerfile_path=""):
    ensure_network_exists()
    ensure_sqlancer_image(force_rebuild=not use_cache)
    cfg = load_json(config_path)

    image = cfg["image"]
    container_name = cfg["container_name"]

    if not use_cache and not custom:
        print(f"[INFO] Pulling image {image}")
        run_command(["docker", "pull", image])

    if custom:
        build_cmd = ["docker", "build", "-t", cfg["image"], os.path.dirname(dockerfile_path)]
        if not use_cache:
            build_cmd.insert(2, "--no-cache")
        run_command(build_cmd)

    start_db_container(dbms, config_path)

    return cfg, container_name


def test_single(dbms, config_path, use_cache=False):
    cfg, container_name = build_environment(dbms, config_path, use_cache)

    start_sqlancer_container(
        dbms=dbms,
        host_container_name=container_name,
        username=cfg["username"],
        password=cfg["password"],
        oracle=cfg["oracle"],
        threads=cfg["num_threads"],
        timeout=cfg["timeout_seconds"]
    )


def test_all(use_cache=False):
    global_cfg = load_json("config.json")
    dbms_list = global_cfg.get("dbms_list", [])
    for dbms in dbms_list:
        config_path = os.path.join(dbms, "config.json")
        if not os.path.exists(config_path):
            print(f"[WARNING] Skipping {dbms}, missing config file.")
            continue
        test_single(dbms, config_path, use_cache)

def test_custom_dockerfile(dockerfile_path, config_path, use_cache=False):
    cfg = load_json(config_path)
    dbms = cfg["dbms"]
    cfg, container_name = build_environment(dbms, config_path, use_cache, True, dockerfile_path)

    start_sqlancer_container(
        dbms=dbms,
        host_container_name=container_name,
        username=cfg["username"],
        password=cfg["password"],
        oracle=cfg["oracle"],
        threads=cfg["num_threads"],
        timeout=cfg["timeout_seconds"]
    )

def ensure_network_exists(network_name="sqlancer-net"):
    try:
        output = subprocess.check_output([
            "docker", "network", "ls",
            "--filter", f"name={network_name}",
            "--format", "{{.Name}}"
        ])
        networks = output.decode().splitlines()
        if network_name not in networks:
            print(f"[INFO] Creating docker network: {network_name}")
            subprocess.run(["docker", "network", "create", network_name], check=True)
        else:
            print(f"[INFO] Docker network '{network_name}' already exists.")
    except Exception as e:
        print(f"[ERROR] Failed to check/create Docker network: {e}")
        sys.exit(1)
