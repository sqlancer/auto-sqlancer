import subprocess

def exec_sql_script(container_name, root_password, sql_script_path):
    cmd = f"sudo docker exec -i {container_name} mysql -uroot -p{root_password} < {sql_script_path}"
    print(f"[DB] Executing SQL script with command: {cmd}")
    subprocess.run(cmd, shell=True, check=True)
