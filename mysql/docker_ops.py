import subprocess

def pull_docker_image(version: str):
    image = f"mysql:{version}"
    print(f"[MySQL] Pulling image {image} …")
    subprocess.run(["sudo", "docker", "pull", image], check=True)
