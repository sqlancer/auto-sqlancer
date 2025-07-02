import argparse
import subprocess
import json
import os

CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def run_docker_build(image_name, dbms, version):
    print(f"=== [STEP] Generating Dockerfile for {dbms}:{version} ===")
    subprocess.run(["python3", "generate_dockerfile.py", dbms, version], check=True)
    print(f"=== [STEP] Building image: {image_name} ===")
    subprocess.run(["sudo", "docker", "build", "-t", image_name, "."], check=True)
    print(f"=== [STEP] Pulling DBMS image: {dbms}:{version} ===")
    subprocess.run(["python3", "-c", f"import {dbms}.docker_ops as db; db.pull_docker_image('{version}')"], check=True)

def run_test(dbms, version, threads, timeout, oracle, password, username):
    image_name = f"sqlancer-auto-{dbms}-{version.replace('.', '-')}"
    run_docker_build(image_name, dbms, version)

    print(f"=== [INFO] Running SQLancer test for {dbms} ===")
    subprocess.run([
        "sudo", "docker", "run", "--rm",
        "-e", f"DBMS={dbms}",
        "-e", f"VERSION={version}",
        "-e", f"SQLANCER_THREADS={threads}",
        "-e", f"SQLANCER_TIMEOUT={timeout}",
        "-e", f"SQLANCER_ORACLE={oracle}",
        "-e", f"SQLANCER_USERNAME={username}",
        "-e", f"SQLANCER_PASSWORD={password}",
        image_name
    ], check=True)

def main():
    config = load_config()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode")

    test_parser = subparsers.add_parser("test-db")
    test_parser.add_argument("dbms")
    test_parser.add_argument("version")
    test_parser.add_argument("--num-threads", type=int, default=config["num_threads"])
    test_parser.add_argument("--timeout-seconds", type=int, default=config["timeout_seconds"])
    test_parser.add_argument("--oracle", default=config["oracle"])
    test_parser.add_argument("--password", default=config["password"])

    test_all_parser = subparsers.add_parser("test-all")
    test_all_parser.add_argument("--num-threads", type=int, default=config["num_threads"])
    test_all_parser.add_argument("--timeout-seconds", type=int, default=config["timeout_seconds"])
    test_all_parser.add_argument("--oracle", default=config["oracle"])
    test_all_parser.add_argument("--password", default=config["password"])

    docker_parser = subparsers.add_parser("docker")
    docker_parser.add_argument("-name", required=True)
    docker_parser.add_argument("-db", nargs=2, metavar=("DBMS", "VERSION"), required=True)

    args = parser.parse_args()

    if args.mode == "test-db":
        username = config["usernames"].get(args.dbms)
        if not username:
            raise ValueError(f"No username specified in config for DBMS: {args.dbms}")
        run_test(args.dbms, args.version, args.num_threads, args.timeout_seconds, args.oracle, args.password, username)

    elif args.mode == "test-all":
        for dir in os.listdir():
            if os.path.isdir(dir) and os.path.exists(f"{dir}/docker_ops.py"):
                version = config["versions"].get(dir)
                username = config["usernames"].get(dir)
                if version and username:
                    run_test(dir, version, args.num_threads, args.timeout_seconds, args.oracle, args.password, username)

    elif args.mode == "docker":
        run_docker_build(args.name, args.db[0], args.db[1])

if __name__ == "__main__":
    main()
