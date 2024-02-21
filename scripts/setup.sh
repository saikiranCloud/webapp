#!/bin/bash
# Install application-specific dependencies
# sudo dnf update -y
sudo dnf install -y unzip
sudo dnf install python3 python3-pip
echo "after python"
sudo yum install -y mysql-server
echo "after mysql"
sudo systemctl start mysqld
sudo systemctl enable mysqld
echo "enabled"
sudo mysql -u root -e "CREATE DATABASE IF NOT EXISTS cloud;"
sudo mysql -u root -e "CREATE USER IF NOT EXISTS clouddev@'localhost' IDENTIFIED BY 'Cloud123';"
sudo mysql -u root -e "GRANT ALL PRIVILEGES ON cloud.* TO clouddev@'localhost';"
sudo mysql -u root -e "FLUSH PRIVILEGES;"