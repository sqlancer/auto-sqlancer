import os
import sys
import subprocess

def build_sqlancer():
    subprocess.run(["docker", "build", "-t", "sqlancer:latest", "./sqlancer"], check=True)

def build_db(dbms, version):
    tag = f"{dbms}:{version}"
    subprocess.run(["docker", "pull", tag], check=True)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sqlancer":
        build_sqlancer()
    elif cmd == "db":
        dbms = sys.argv[2]
        version = sys.argv[4]
        build_db(dbms, version)
