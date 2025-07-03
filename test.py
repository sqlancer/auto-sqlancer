import argparse
import json
import os
import subprocess

GLOBAL_CONFIG = "config.json"

def load_json(path):
    with open(path) as f:
        return json.load(f)

def run_docker_build(dbms, version):
    image = f"{dbms}-{version.replace('.', '-')}"
    print(f"[INFO] Building image for {dbms}:{version}")
    subprocess.run(["python3", "generate_dockerfile.py", dbms, version], check=True)
    subprocess.run(["sudo", "docker", "build", "-t", image, ".", "--build-arg", f"VERSION={version}"], check=True)
    subprocess.run(["python3", "-c",
        f"import {dbms}.docker_ops as db; db.pull_docker_image('{version}')"], check=True)
    return image

def run_test(dbms, cfg):
    image = f"{dbms}-{cfg['version'].replace('.', '-')}"
    print(f"[INFO] Running test for {dbms}:{cfg['version']}")
    subprocess.run([
        "sudo", "docker", "compose", "run", "--rm", "--name", f"{dbms}-sqlancer",
        "-e", f"DBMS={dbms}",
        "-e", f"VERSION={cfg['version']}",
        "-e", f"SQLANCER_THREADS={cfg['num_threads']}",
        "-e", f"SQLANCER_TIMEOUT={cfg['timeout_seconds']}",
        "-e", f"SQLANCER_ORACLE={cfg['oracle']}",
        "-e", f"SQLANCER_USERNAME={cfg['username']}",
        "-e", f"SQLANCER_PASSWORD={cfg['password']}",
        "sqlancer"
    ], check=True)

def main():
    glob = load_json(GLOBAL_CONFIG)
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode")

    # test-db command
    p1 = sub.add_parser("test-db")
    p1.add_argument("dbms")
    p1.add_argument("--version", required=True)
    p1.add_argument("--num-threads", type=int)
    p1.add_argument("--timeout-seconds", type=int)
    p1.add_argument("--oracle")
    p1.add_argument("--username")
    p1.add_argument("--password")

    # test-all command
    sub.add_parser("test-all")

    # docker build command
    p3 = sub.add_parser("docker")
    p3.add_argument("dbms")
    p3.add_argument("--version", required=True)

    args = parser.parse_args()

    if args.mode == "test-db":
        if args.dbms not in glob["dbms_list"]:
            raise ValueError(f"Unknown DBMS: {args.dbms}")
        cfg = load_json(os.path.join(args.dbms, "config.json"))
        cfg["version"] = args.version
        if args.num_threads: cfg["num_threads"] = args.num_threads
        if args.timeout_seconds: cfg["timeout_seconds"] = args.timeout_seconds
        if args.oracle: cfg["oracle"] = args.oracle
        if args.username: cfg["username"] = args.username
        if args.password: cfg["password"] = args.password
        run_test(args.dbms, cfg)

    elif args.mode == "test-all":
        for db in glob["dbms_list"]:
            path = os.path.join(db, "config.json")
            if os.path.exists(path):
                run_test(db, load_json(path))
            else:
                print(f"[WARN] Skipped {db}: config.json not found.")

    elif args.mode == "docker":
        if args.dbms not in glob["dbms_list"]:
            raise ValueError(f"Unknown DBMS: {args.dbms}")
        run_docker_build(args.dbms, args.version)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
