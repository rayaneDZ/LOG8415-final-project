import paramiko
import time
import sys
import json
from scp import SCPClient

with open('collected_data.json', 'r') as openfile:
    # Reading from json file
    json_object = json.load(openfile)
    openfile.close()

public_ip_address = json_object["mgmt_node"]["PublicIpAddress"]
private_ip_address = json_object["mgmt_node"]["PrivateIpAddress"]
private_ip_address_data_1 = json_object["data_node_1"]["PrivateIpAddress"]
private_ip_address_data_2 = json_object["data_node_2"]["PrivateIpAddress"]
private_ip_address_data_3 = json_object["data_node_3"]["PrivateIpAddress"]

f = open("config.ini", "a")

f.write("[ndb_mgmd]\n")
f.write("hostname=" + private_ip_address)
f.write("\ndatadir=/var/lib/mysql-cluster")
f.write("\nnodeid=1\n")

f.write("[ndbd default]\n")
f.write("noofreplicas=3\n")

f.write("[ndbd]\n")
f.write("hostname=" + private_ip_address_data_1)
f.write("\ndatadir=/usr/local/mysql/data")
f.write("\nnodeid=2\n")

f.write("[ndbd]\n")
f.write("hostname=" + private_ip_address_data_2)
f.write("\ndatadir=/usr/local/mysql/data")
f.write("\nnodeid=3\n")

f.write("[ndbd]\n")
f.write("hostname=" + private_ip_address_data_3)
f.write("\ndatadir=/usr/local/mysql/data")
f.write("\nnodeid=4\n")

f.write("[mysqld]\n")
f.write("hostname=" + private_ip_address)

f.close()

f2 = open("my.cnf", "a")

f2.write("[mysqld]\n")
f2.write("ndbcluster\n")
f2.write("[mysql_cluster]\n")
f2.write("ndb-connectstring=" + private_ip_address + "\n")

f2.close()


def mgmd_commands():
    return """
#!/bin/bash

wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

sudo dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

sudo mkdir /var/lib/mysql-cluster

sudo cp /home/ubuntu/config.ini /var/lib/mysql-cluster/config.ini

sudo ndb_mgmd -f /var/lib/mysql-cluster/config.ini >> /home/ubuntu/mgmdLog.txt

sudo ufw allow from """+private_ip_address+"""
sudo ufw allow from """+private_ip_address_data_1+"""
sudo ufw allow from """+private_ip_address_data_2+"""
sudo ufw allow from """+private_ip_address_data_3+"""

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


def start_mgmd(public_ip_address):

    # Setting Up SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_connect_with_retry(ssh, public_ip_address, 0)
    print("Connected through SSH!")

    print('uploading config.ini file')
    scp = SCPClient(ssh.get_transport())
    scp.put(
        "config.ini",
        remote_path="/home/ubuntu",
        recursive=True
    )
    scp.put(
        "my.cnf",
        remote_path="/home/ubuntu",
        recursive=True
    )
    print('Done uploading')

    time.sleep(3)

    stdin, stdout, stderr = ssh.exec_command(mgmd_commands())
    old_stdout = sys.stdout
    log_file = open("mgmd-logfile.log", "w")
    print('mgmd env setup done \n stdout:', stdout.read(), file=log_file)
    log_file.close()

    scp.close()
    ssh.close()


print("\n############### Starting MGMD process on Management Node ###############\n")

start_mgmd(public_ip_address)

print("############### MGMD Started! ###############")
