import json

with open("config.json") as f:
    config = json.load(f)

dbms = config.get("dbms", "").lower()

dbms_packages = {
    "mysql": "mysql-server",
    "postgres": "postgresql",
}

if dbms not in dbms_packages:
    raise ValueError(f"Unsupported DBMS: {dbms}")

with open("Dockerfile.template") as f:
    template = f.read()

final_dockerfile = template.replace("{{DBMS_PACKAGE}}", dbms_packages[dbms])

with open("Dockerfile", "w") as f:
    f.write(final_dockerfile)

print(f"[✔] Dockerfile generated for DBMS: {dbms}")
