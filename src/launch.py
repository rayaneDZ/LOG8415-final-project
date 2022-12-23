import os

os.system("python setup.py")
os.system("python standalone-benchmark.py")
os.system("python start-mgmd.py")
os.system("python start-ndbd.py")
os.system("python start-mysql.py")

print(
    "Now connected to the management node using its public Ipv4 DNS using this command: ssh -i labsuser.pem ubuntu@[public dns]")
print("Then run the following commands on the management node step by step")
print("AND leave the password blank when prompted")

print("sudo apt install -y libaio1 libmecab2")
print("cd /home/ubuntu/install")
print("sudo dpkg -i mysql-common_7.6.6-1ubuntu18.04_amd64.deb")
print("sudo dpkg -i mysql-cluster-community-client_7.6.6-1ubuntu18.04_amd64.deb")
print("sudo dpkg -i mysql-client_7.6.6-1ubuntu18.04_amd64.deb")

# the following command requires user input
print("cd /home/ubuntu/install")
print("sudo dpkg -i mysql-cluster-community-server_7.6.6-1ubuntu18.04_amd64.deb")
print("sudo dpkg -i mysql-server_7.6.6-1ubuntu18.04_amd64.deb")
print("cat /home/ubuntu/my.cnf | sudo tee /etc/mysql/my.cnf")
print("sudo systemctl restart mysql")
print("sudo systemctl enable mysql")

print("after this, cd to src/, then launch the cluster-benchmark.py script to benchmark your cluster")
