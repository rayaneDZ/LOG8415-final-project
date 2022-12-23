import paramiko
import time
import sys
import json

with open('collected_data.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)
    openfile.close()

public_ip_address = json_object["mgmt_node"]["PublicIpAddress"]
private_ip_address = json_object["mgmt_node"]["PrivateIpAddress"]


def mysql_commands():
    return """
#!/bin/bash

wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar

mkdir install

tar -xvf mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar -C install/

sudo apt update

sudo apt install -y libaio1 libmecab2

cd /home/ubuntu/install

sudo dpkg -i mysql-common_7.6.6-1ubuntu18.04_amd64.deb

sudo dpkg -i mysql-cluster-community-client_7.6.6-1ubuntu18.04_amd64.deb

sudo dpkg -i mysql-client_7.6.6-1ubuntu18.04_amd64.deb

EOF
"""


def ssh_connect_with_retry(ssh, public_ip_address, retries):
    """
    ssh: paramiko SSHClient instance
    public_ip_address: ip of the instance we wish to connect to
    retries: number of tries before failing to connect
    """
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


def start_mysql(public_ip_address):
    """
    this functions connects to the management node and install MySQL Server and Client
    only half of the steps are done by this function because the next command needs a user input (see launch.py)
    """
    # Setting Up SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_connect_with_retry(ssh, public_ip_address, 0)
    print("Connected through SSH!")

    stdin, stdout, stderr = ssh.exec_command(mysql_commands())
    old_stdout = sys.stdout
    log_file = open("mysql-logfile.log", "w")
    print('mysql env setup done \n stdout:', stdout.read(), file=log_file)
    log_file.close()

    ssh.close()


print("\n############### Starting MySQL Server/Client process on Management Node ###############\n")

start_mysql(public_ip_address)

print("############### MySQL Started! ###############")
