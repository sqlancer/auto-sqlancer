import os
import sys
import subprocess
import logging
from utils import run_command

def build_sqlancer_image(script_log, docker_log, force_rebuild=False):
    if force_rebuild:
        script_log.info("Rebuilding SQLancer image: sqlancer:latest ...")
        run_command(["docker", "build", "--no-cache", "-t", "sqlancer:latest", "./sqlancer"], docker_log)
        script_log.info("SQLancer image built: sqlancer:latest")
        return

    result = subprocess.run(
        ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
        capture_output=True, text=True
    )
    images = result.stdout.strip().splitlines()
    if "sqlancer:latest" in images:
        script_log.info("SQLancer image exists: sqlancer:latest")
    else:
        script_log.info("Building SQLancer image from cache: sqlancer:latest...")
        run_command(["docker", "build", "-t", "sqlancer:latest", "./sqlancer"], docker_log)
        script_log.info("SQLancer image built: sqlancer:latest")

def build_network(script_log, docker_log, network_name="sqlancer-net"):
    try:
        output = subprocess.check_output([
            "docker", "network", "ls",
            "--filter", f"name={network_name}",
            "--format", "{{.Name}}"
        ])
        networks = output.decode().splitlines()
        if network_name not in networks:
            script_log.info("Building network: %s ...", network_name)
            run_command(["docker", "network", "create", network_name], docker_log)
            script_log.info("Network built: %s", network_name)
        else:
            script_log.info("Network already exists: %s", network_name)
            
    except Exception as e:
        script_log.error("Network building failed: %s", network_name)
        sys.exit(1)

def build_db_image(cfg, use_cache, script_log, docker_log, custom=False, dockerfile_path=""):
    if not use_cache and not custom:
        image = cfg["image"]
        script_log.info("Pulling db image: %s ...", image)
        run_command(["docker", "pull", image], docker_log)
        script_log.info("DB image pulled: %s", image)
    elif custom:
        build_cmd = ["docker", "build", "-t", cfg["image"], os.path.dirname(dockerfile_path)]
        if not use_cache:
            build_cmd.insert(2, "--no-cache")
        script_log.info("Building db image: %s ...", cfg["image"])
        run_command(build_cmd, docker_log)
        script_log.info("DB image built: %s ...", cfg["image"])
    else:
        script_log.info("DB image already exists: %s", cfg["image"])

def build_environment(cfg, use_cache, script_log, docker_log, custom=False, dockerfile_path=""):
    script_log.info("==============================Building environment==============================")
    build_network(script_log, docker_log)
    build_sqlancer_image(script_log, docker_log, force_rebuild=False)
    if cfg["embedded"] == "no":
        build_db_image(cfg, use_cache, script_log, docker_log, custom, dockerfile_path)
    script_log.info("==============================Building environment==============================")
    