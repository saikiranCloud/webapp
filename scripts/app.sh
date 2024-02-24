#!/bin/bash
echo "in app.sh"
sudo mkdir /opt/webapp

sudo mv /tmp/webapp.zip /opt/webapp


sudo unzip /opt/webapp/webapp.zip -d /opt/webapp

sudo rm /opt/webapp/webapp.zip

sudo python3 -m venv venv
source venv/bin/activate 

pwd

ls

cd venv 

sudo python3 -m pip install --upgrade pip

sudo pip3 install setuptools-rust bcrypt blinker certifi cffi charset-normalizer click colorama cryptography Flask Flask-Bcrypt Flask-HTTPAuth Flask-SQLAlchemy greenlet idna iniconfig itsdangerous Jinja2 MarkupSafe packaging pluggy pycparser PyJWT PyMySQL pytest python-dotenv regex requests SQLAlchemy typing_extensions urllib3 uuid Werkzeug

sudo chown -R csye6225:csye6225 /opt/webapp/

sudo cp /tmp/webapp.service /etc/systemd/system/webapp.service

sudo systemctl daemon-reload
sudo systemctl enable webapp
sudo systemctl start webapp
