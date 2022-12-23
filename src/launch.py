import os

os.system("python setup.py")
os.system("python standalone-benchmark.py")
os.system("python start-mgmd.py")
os.system("python start-ndbd.py")
os.system("python start-mysql.py")

print("SSH into the management node and run the following commands:")
print("*NOTE*: leave the password for mysql blank when prompted")

print("command 1: cd /home/ubuntu/install")
# the following command requires user input
print("command 2: sudo dpkg -i mysql-cluster-community-server_7.6.6-1ubuntu18.04_amd64.deb")
print("command 3: sudo dpkg -i mysql-server_7.6.6-1ubuntu18.04_amd64.deb")
print("command 4: cat /home/ubuntu/my.cnf | sudo tee /etc/mysql/my.cnf")
print("command 5: sudo systemctl restart mysql")
print("command 6: sudo systemctl enable mysql")

print("You can now disconnect from the management node and go back to your local machine")
print("On your local machine, change directory to src/ then launch the 'cluster-benchmark.py' script to benchmark your cluster")
