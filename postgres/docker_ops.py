import subprocess

def pull_docker_image(version: str):
    image = f"postgres:{version}"
    print(f"[PostgreSQL] Pulling image {image} …")
    subprocess.run(["sudo", "docker", "pull", image], check=True)
