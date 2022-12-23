import paramiko
import time
import sys
import json
from scp import SCPClient

with open('collected_data.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)
    openfile.close()

public_ip_address = json_object["stand-alone_node"]["PublicIpAddress"]


def stand_alone_commands():
    return """
#!/bin/bash

#updating and upgrading the packages
sudo apt update -y
sudo apt upgrade -y

#installing mysql server
sudo apt-get install mysql-server -y

#downloading sakila database SQL files
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xzvf sakila-db.tar.gz
rm sakila-db.tar.gz

#create the schema and the tables
sudo mysql --defaults-file=/etc/mysql/debian.cnf < /home/ubuntu/sakila-db/sakila-schema.sql

#populate the database
sudo mysql --defaults-file=/etc/mysql/debian.cnf < /home/ubuntu/sakila-db/sakila-data.sql

#installing sysbench
sudo apt-get install sysbench -y

#preparing the benchmark
sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --mysql-user=root --mysql-password= --db-driver=mysql prepare

#running the benchmark
sudo sysbench oltp_read_write --table-size=100000 --num-threads=6 --max-time=60 --mysql-db=sakila --db-driver=mysql --mysql-user=root --mysql-password= run > stand-alone-benchmark.txt

#cleanup
sudo sysbench oltp_read_write --mysql-db=sakila --mysql-user=root --mysql-password= --db-driver=mysql cleanup

EOF
"""


def ssh_connect_with_retry(ssh, public_ip_address, retries):
    if retries > 3:
        return False
    privkey = paramiko.RSAKey.from_private_key_file(
        'labsuser.pem')
    interval = 2
    try:
        retries += 1
        print('SSH into the instance: {}'.format(public_ip_address))
        ssh.connect(hostname=public_ip_address,
                    username="ubuntu", pkey=privkey)
        return True
    except Exception as e:
        print(e)
        time.sleep(interval)
        print('Retrying SSH connection to {}'.format(public_ip_address))
        ssh_connect_with_retry(ssh, public_ip_address, retries)


def stand_alone(public_ip_address):

    # Setting Up SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_connect_with_retry(ssh, public_ip_address, 0)
    print("Connected through SSH!")

    print("Benchmarking the MySQL stand-alone instance...")
    stdin, stdout, stderr = ssh.exec_command(stand_alone_commands())
    old_stdout = sys.stdout
    log_file = open("stand-alone-logfile.log", "w")
    print('stand-alone env setup done \n stdout:', stdout.read(), file=log_file)
    log_file.close()

    print('Retrieving results file')
    scp = SCPClient(ssh.get_transport())
    scp.get('/home/ubuntu/stand-alone-benchmark.txt', './')
    print('Results file is in the current folder')

    scp.close()
    ssh.close()


print("\n############### Installing MySQL and Sakila DB and Sysbench on stand-alone node ###############\n")

stand_alone(public_ip_address)

print("############### Stand-alone Benchmarking DONE! ###############")
