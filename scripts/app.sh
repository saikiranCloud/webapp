#!/bin/bash
echo "in app.sh"
sudo mkdir /home/csye6225/webapp_main

sudo mv ~/webapp.zip /home/csye6225/webapp_main

sudo unzip /home/csye6225/webapp_main/webapp.zip -d /home/csye6225/webapp_main

sudo rm /home/csye6225/webapp_main/webapp.zip

sudo python3 -m venv venv
source venv/bin/activate 

pwd

ls
sudo python3 -m pip install --upgrade pip

sudo pip3 install setuptools-rust bcrypt blinker certifi cffi charset-normalizer click colorama cryptography Flask Flask-Bcrypt Flask-HTTPAuth Flask-SQLAlchemy greenlet idna iniconfig itsdangerous Jinja2 MarkupSafe packaging pluggy pycparser PyJWT PyMySQL pytest python-dotenv regex requests SQLAlchemy typing_extensions urllib3 uuid Werkzeug

sudo chown -R csye6225:csye6225 /home/csye6225/webapp_main/

sudo cp /home/csye6225/webapp_main/webapp/webapp.service /etc/systemd/system/webapp.service

sudo systemctl daemon-reload
sudo systemctl enable webapp
