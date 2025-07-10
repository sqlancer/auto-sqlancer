import argparse, json, os, subprocess, yaml, string

GLOBAL = "config.json"
OVERRIDE = "docker-compose.override.yml"

def load_json(path):
    with open(path) as f: return json.load(f)

def build_service(db, cfg):
    tag = f"{db}-{cfg['version']}"
    env = {
        "VERSION": cfg["version"],
        db.upper() + "_USERNAME": cfg["username"],
        db.upper() + "_PASSWORD": cfg["password"],
        "TAG": tag
    }
    raw = json.dumps(cfg["docker"])
    filled = string.Template(raw).safe_substitute(env)
    return tag, json.loads(filled)

def generate_env_and_override(selected, cfg_map):
    env = {}
    services = {}
    for db in selected:
        cfg = cfg_map[db]
        tag, svc = build_service(db, cfg)
        services[tag] = svc
        # env entries
        env[f"{db.upper()}_VERSION"] = cfg["version"]
        env[f"{db.upper()}_USERNAME"] = cfg["username"]
        env[f"{db.upper()}_PASSWORD"] = cfg["password"]

    db0 = selected[0]
    cfg0 = cfg_map[db0]
    env["SQLANCER_THREADS"] = str(cfg0["num_threads"])
    env["SQLANCER_TIMEOUT"] = str(cfg0["timeout_seconds"])
    env["SQLANCER_ORACLE"] = cfg0["oracle"]
    env["SQLANCER_USERNAME"] = cfg0["username"]
    env["SQLANCER_PASSWORD"] = cfg0["password"]
    env["SQLANCER_DBMS"] = db0
    env["SQLANCER_HOST"] = f"{db0}-{cfg0['version']}"

    # generate env file
    with open(".env", "w") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")
    print("[INFO] .env written:", env.keys())

    # add sqlancer service
    services["sqlancer"] = {
        "build": {"context": "./sqlancer"},
        "container_name": "sqlancer",
        "env_file": ".env",
        "depends_on": [f"{db}-{cfg_map[db]['version']}" for db in selected],
        "command": ["/root/entrypoint.sh"]
    }

    with open(OVERRIDE, "w") as f:
        yaml.dump({"services": services}, f, sort_keys=False)
    print("[INFO] override generated for services:", list(services.keys()))

def run_compose():
    subprocess.run([
        "sudo", "docker", "compose", "-f", "docker-compose.yml", "-f", OVERRIDE,
        "up", "--build", "--abort-on-container-exit", "--remove-orphans"
    ], check=True)

def main():
    glob = load_json(GLOBAL)
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="mode")

    t = sub.add_parser("test-db")
    t.add_argument("dbms")
    t.add_argument("--version", required=True)
    t.add_argument("--num-threads", type=int)
    t.add_argument("--timeout-seconds", type=int)
    t.add_argument("--oracle")
    t.add_argument("--username")
    t.add_argument("--password")

    sub.add_parser("test-all")

    args = p.parse_args()
    if args.mode == "test-db":
        db = args.dbms
        if db not in glob["dbms_list"]: raise ValueError("Unknown DBMS")
        cfg = load_json(f"{db}/config.json")
        cfg["version"] = args.version
        for key in ("num_threads", "timeout_seconds", "oracle", "username", "password"):
            val = getattr(args, key if key != "timeout_seconds" else "timeout_seconds")
            if val: cfg[key] = val
        cfg_map = {db: cfg}
        generate_env_and_override([db], cfg_map)
        run_compose()

    elif args.mode == "test-all":
        for db in glob["dbms_list"]:
            path = os.path.join(db, "config.json")
            if os.path.exists(path):
                cfg = load_json(path)
                cfg_map = {db: cfg}
                print(f"\n[INFO] Testing DBMS: {db}")
                generate_env_and_override([db], cfg_map)
                run_compose()


if __name__ == "__main__":
    main()
