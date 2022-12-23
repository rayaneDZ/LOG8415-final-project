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

public_ip_address_data_1 = json_object["data_node_1"]["PublicIpAddress"]
private_ip_address_data_1 = json_object["data_node_1"]["PrivateIpAddress"]

public_ip_address_data_2 = json_object["data_node_2"]["PublicIpAddress"]
private_ip_address_data_2 = json_object["data_node_2"]["PrivateIpAddress"]

public_ip_address_data_3 = json_object["data_node_3"]["PublicIpAddress"]
private_ip_address_data_3 = json_object["data_node_3"]["PrivateIpAddress"]


def ndbd_commands():
    return """
#!/bin/bash

wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb

sudo apt update

sudo apt install libclass-methodmaker-perl

sudo dpkg -i mysql-cluster-community-data-node_7.6.6-1ubuntu18.04_amd64.deb

echo -e "[mysql_cluster]" >> ./my.cnf
echo -e "ndb-connectstring="""+private_ip_address+""" " >> ./my.cnf
sudo cp ./my.cnf /etc/my.cnf

sudo mkdir -p /usr/local/mysql/data

sudo ndbd >> /home/ubuntu/ndbdLog.txt

sudo ufw allow from """+private_ip_address+"""
sudo ufw allow from """+private_ip_address_data_1+"""
sudo ufw allow from """+private_ip_address_data_2+"""
sudo ufw allow from """+private_ip_address_data_3+"""

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


def start_ndbd(public_ip_address):
    """
    this function connects to the data node and installs the necessary packages to run ndbd process.
    it also configures the /etc/my.cnf file
    """
    # Setting Up SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_connect_with_retry(ssh, public_ip_address, 0)
    print("Connected through SSH!")
    print("Installing NDBD process")
    stdin, stdout, stderr = ssh.exec_command(ndbd_commands())
    old_stdout = sys.stdout
    log_file = open("ndbd-logfile.log", "w")
    print('ndbd env setup done \n stdout:', stdout.read(), file=log_file)
    log_file.close()

    ssh.close()


print("\n############### Starting NDBD Processes on Data Nodes ###############\n")

for ip in [public_ip_address_data_1, public_ip_address_data_2, public_ip_address_data_3]:
    start_ndbd(ip)

print("############### NDBD Started! ###############")
