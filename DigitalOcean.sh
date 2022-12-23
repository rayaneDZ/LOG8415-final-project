###### LINK TO BLOG
#https://www.digitalocean.com/community/tutorials/how-to-create-a-multi-node-mysql-cluster-on-ubuntu-18-04
###################

################
###### MGMT Node
################
wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.0/mysql-cluster-community-management-server_8.0.31-1ubuntu22.04_amd64.deb

sudo dpkg -i mysql-cluster-community-management-server_8.0.31-1ubuntu22.04_amd64.deb

sudo mkdir /var/lib/mysql-cluster
sudo nano /var/lib/mysql-cluster/config.ini

sudo ndb_mgmd -f /var/lib/mysql-cluster/config.ini

#sudo ufw allow from "all of the 3 other nodes"

#################
###### Data Nodes
#################


wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.0/mysql-cluster-community-data-node_8.0.31-1ubuntu22.04_amd64.deb

sudo apt update

sudo apt install libclass-methodmaker-perl

sudo dpkg -i mysql-cluster-community-data-node_8.0.31-1ubuntu22.04_amd64.deb

nano /etc/my.cnf

sudo mkdir -p /usr/local/mysql/data

sudo ndbd

#sudo ufw allow from "all of the 3 other nodes"

################
###### MGMT Node
################

wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-8.0/mysql-cluster_8.0.31-1ubuntu22.04_amd64.deb-bundle.tar

mkdir install

tar -xvf mysql-cluster_8.0.31-1ubuntu22.04_amd64.deb-bundle.tar -C install/

cd install

sudo apt update

sudo apt install libaio1 libmecab2 

sudo dpkg -i mysql-common_8.0.31-1ubuntu22.04_amd64.deb

sudo dpkg -i mysql-cluster-community-client-plugins_8.0.31-1ubuntu22.04_amd64.deb
sudo dpkg -i mysql-cluster-community-client-core_8.0.31-1ubuntu22.04_amd64.deb
sudo dpkg -i mysql-cluster-community-client_8.0.31-1ubuntu22.04_amd64.deb
sudo dpkg -i mysql-client_8.0.31-1ubuntu22.04_amd64.deb

sudo dpkg -i mysql-cluster-community-server-core_8.0.31-1ubuntu22.04_amd64.deb
sudo dpkg -i mysql-cluster-community-server_8.0.31-1ubuntu22.04_amd64.deb

sudo dpkg -i mysql-server_8.0.31-1ubuntu22.04_amd64.deb

sudo echo -e "[mysqld]\nndbcluster\n[mysql_cluster]\nndb-connectstring=[Ip]" >> /etc/mysql/my.cnf

sudo systemctl restart mysql

sudo systemctl enable mysql
