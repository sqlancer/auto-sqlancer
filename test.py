import argparse
import json
import os
import subprocess

GLOBAL_CONFIG = "config.json"

def load_json(path):
    with open(path) as f:
        return json.load(f)

def run_docker_build(dbms, version):
    image = f"sqlancer-auto-{dbms}-{version.replace('.', '-')}"
    print(f"=== [STEP] Generating Dockerfile for {dbms}:{version} ===")
    subprocess.run(["python3", "generate_dockerfile.py", dbms, version], check=True)
    print(f"=== [STEP] Building image: {image} ===")
    subprocess.run(["sudo", "docker", "build", "-t", image, "."], check=True)
    print(f"=== [STEP] Pulling DBMS image: {dbms}:{version} ===")
    subprocess.run(["python3", "-c", f"import {dbms}.docker_ops as db; db.pull_docker_image('{version}')"], check=True)
    return image

def run_test(dbms, version, threads, timeout, oracle, username, password):
    image = run_docker_build(dbms, version)
    print(f"=== [INFO] Running SQLancer test for {dbms}:{version} ===")
    subprocess.run([
        "sudo", "docker", "run", "--rm",
        "-e", f"DBMS={dbms}",
        "-e", f"VERSION={version}",
        "-e", f"SQLANCER_THREADS={threads}",
        "-e", f"SQLANCER_TIMEOUT={timeout}",
        "-e", f"SQLANCER_ORACLE={oracle}",
        "-e", f"SQLANCER_USERNAME={username}",
        "-e", f"SQLANCER_PASSWORD={password}",
        image
    ], check=True)

def main():
    glob = load_json(GLOBAL_CONFIG)
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode")

    # python3 test.py test-db [DBMS] [--version VERSION] [--num-threads N] [--timeout-seconds T] [--oracle ORACLE] [--username USER] [--password PASS]
    p1 = sub.add_parser("test-db")
    p1.add_argument("dbms", help="Which DBMS to test")
    p1.add_argument("--version", required=False, help="DBMS version, override config")
    p1.add_argument("--num-threads", type=int, help="SQLancer threads")
    p1.add_argument("--timeout-seconds", type=int, help="SQLancer timeout")
    p1.add_argument("--oracle", help="SQLancer oracle")
    p1.add_argument("--username", help="DB username")
    p1.add_argument("--password", help="DB password")

    # python3 test.py test-all
    sub.add_parser("test-all")

    # python3 test.py docker [DBMS] [--version VERSION] 
    p3 = sub.add_parser("docker")
    p3.add_argument("dbms", help="Which DBMS to build image for")
    p3.add_argument("--version", required=False, help="DBMS version override")

    args = parser.parse_args()

    if args.mode == "test-db":
        if args.dbms not in glob["dbms_list"]:
            raise ValueError(f"Unknown DBMS: {args.dbms}")
        cfg = load_json(os.path.join(args.dbms, "config.json"))
        ver = args.version or cfg["version"]
        threads = args.num_threads or cfg.get("num_threads")
        timeout = args.timeout_seconds or cfg.get("timeout_seconds")
        oracle = args.oracle or cfg.get("oracle")
        username = args.username or cfg.get("username")
        password = args.password or cfg.get("password")
        run_test(args.dbms, ver, threads, timeout, oracle, username, password)

    elif args.mode == "test-all":
        for db in glob["dbms_list"]:
            cfgpath = os.path.join(db, "config.json")
            if os.path.exists(cfgpath):
                cfg = load_json(cfgpath)
                run_test(db, cfg["version"], cfg["num_threads"], cfg["timeout_seconds"],
                         cfg["oracle"], cfg["username"], cfg["password"])
            else:
                print(f"Skipped {db}: missing config.json")

    elif args.mode == "docker":
        if args.dbms not in glob["dbms_list"]:
            raise ValueError(f"Unknown DBMS: {args.dbms}")
        cfg = load_json(os.path.join(args.dbms, "config.json"))
        ver = args.version or cfg["version"]
        run_docker_build(args.dbms, ver)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
