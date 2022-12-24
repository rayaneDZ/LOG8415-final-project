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


def cluster_commands():
    return """
#!/bin/bash

#downloading sakila database SQL files
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xzvf sakila-db.tar.gz
rm sakila-db.tar.gz

#modify sakila-schema.sql to not use InnoDB
sed -i 's/ENGINE=InnoDB//g' /home/ubuntu/sakila-db/sakila-schema.sql

#create the schema and the tables
sudo mysql < /home/ubuntu/sakila-db/sakila-schema.sql

#populate the database
sudo mysql < /home/ubuntu/sakila-db/sakila-data.sql

#installing sysbench
sudo apt-get install sysbench -y

sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --mysql-user=root --mysql-password= --db-driver=mysql --mysql-storage-engine=ndbcluster prepare
sudo sysbench oltp_read_write --table-size=100000 --num-threads=6 --max-time=60 --mysql-db=sakila --mysql-user=root --mysql-password= --db-driver=mysql --mysql-storage-engine=ndbcluster run > cluster-benchmark.txt
sudo sysbench oltp_read_write --mysql-db=sakila --mysql-user=root --mysql-password= --db-driver=mysql --mysql-storage-engine=ndbcluster cleanup


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


def cluster_benchmark(public_ip_address):
    """
    this function connects to the management node,
    installs sakila-db
    installs sysbench
    runs the benchmarking using sysbench then retrieves the results file and puts it in the src/ directory
    """
    # Setting Up SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_connect_with_retry(ssh, public_ip_address, 0)
    print("Connected through SSH!")
    print("Installing Sakila DB on the cluster and running the benchmark using Sysbench")
    stdin, stdout, stderr = ssh.exec_command(cluster_commands())
    old_stdout = sys.stdout
    log_file = open("mysql-logfile.log", "w")
    print('mysql env setup done \n stdout:', stdout.read(), file=log_file)
    log_file.close()

    print('Retrieving results file')
    scp = SCPClient(ssh.get_transport())
    scp.get('/home/ubuntu/cluster-benchmark.txt', './')
    print('Results file is in the current folder')

    scp.close()
    ssh.close()


print("\n############### Starting To Benchmark the MySQL Cluster ###############\n")

cluster_benchmark(public_ip_address)

print("############### Benchmark Finished! ###############")
