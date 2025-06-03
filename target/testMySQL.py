#!/usr/bin/env python3
import subprocess
import time

# Dockerfile：MySQL 8.0
dockerfile_content = """\
FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=12345678

EXPOSE 3306

CMD ["mysqld"]
"""

# write Dockerfile 
dockerfile_name = "Dockerfile"
with open(dockerfile_name, "w") as f:
    f.write(dockerfile_content)
print("--------------------Dockerfile generated!--------------------")

# Build docker
build_command = "sudo docker build -t my_mysql ."
print("--------------------start building docker, command: ", build_command)
subprocess.run(build_command, shell=True, check=True)
print("--------------------built docker successfully--------------------")

# run docker
run_command = "sudo docker run -d -p 3306:3306 --name my_mysql_container my_mysql"
print("--------------------start running docker, command: ", run_command)
subprocess.run(run_command, shell=True, check=True)
print("--------------------docker running successfully--------------------")

# wait for mysql starting
time.sleep(60)

# executing scripts
import_sql_command = "sudo docker exec -i my_mysql_container mysql -uroot -p12345678 < /home/vm/run.sql"
print("--------------------execting SQL scripts: ", import_sql_command)
subprocess.run(import_sql_command, shell=True, check=True)
print("--------------------executing exripts successfully--------------------")

# run sqlancer
java_command = ("java -jar sqlancer-*.jar --num-threads 4 --timeout-seconds 60 "
                "--username root --password 12345678 mysql --oracle FUZZER")
print("using SQLAncer to test MySQL", java_command)
subprocess.run(java_command, shell=True, check=True)
print("test completed")
