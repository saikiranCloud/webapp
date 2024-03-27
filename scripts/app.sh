#!/bin/bash
echo "in app.sh"
sudo mkdir /opt/webapp
sudo mkdir -p /var/log/webapp
sudo chown -R csye6225:csye6225 /var/log/webapp

sudo mv /tmp/webapp.zip /opt/webapp


sudo unzip /opt/webapp/webapp.zip -d /opt/webapp

sudo rm /opt/webapp/webapp.zip
sudo chown -R csye6225:csye6225 /opt/webapp/
sudo python3 -m venv venv
source venv/bin/activate 

pwd

ls

cd venv 

sudo python3.8 -m pip install --upgrade pip

sudo pip3.8 install setuptools-rust bcrypt blinker certifi cffi charset-normalizer click colorama cryptography Flask Flask-Bcrypt Flask-HTTPAuth Flask-SQLAlchemy greenlet idna iniconfig itsdangerous Jinja2 MarkupSafe packaging pluggy pycparser PyJWT PyMySQL pytest python-dotenv regex requests SQLAlchemy typing_extensions urllib3 uuid Werkzeug python-json-logger google-api-core google-auth google-cloud-pubsub googleapis-common-protos grpc-google-iam-v1 grpcio grpcio-status proto-plus protobuf pyasn1 pyasn1-modules rsa

sudo cp /tmp/webapp.service /etc/systemd/system/webapp.service
sudo cat /opt/webapp/config.yaml | sudo tee -a /etc/google-cloud-ops-agent/config.yaml > /dev/null

sudo systemctl restart google-cloud-ops-agent
sudo systemctl daemon-reload
sudo systemctl enable webapp
sudo systemctl start webapp