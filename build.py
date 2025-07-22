import os
import sys
import subprocess

def run_command(cmd, **kwargs):
    print("[CMD]", " ".join(cmd))
    subprocess.run(cmd, check=True, **kwargs)

def build_sqlancer_image(force_rebuild=False):
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

def build_network(network_name="sqlancer-net"):
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

def build_db_image(cfg, use_cache, custom=False, dockerfile_path=""):
    if not use_cache and not custom:
        image = cfg["image"]
        print(f"[INFO] Pulling image {image}")
        run_command(["docker", "pull", image])

    if custom:
        build_cmd = ["docker", "build", "-t", cfg["image"], os.path.dirname(dockerfile_path)]
        if not use_cache:
            build_cmd.insert(2, "--no-cache")
        run_command(build_cmd)

def build_environment(cfg, use_cache, custom=False, dockerfile_path=""):
    build_network()
    # build_sqlancer_image(force_rebuild=not use_cache)
    build_sqlancer_image(False)
    if cfg["embedded"] == "no":
        build_db_image(cfg, use_cache, custom, dockerfile_path)
    
