import os,time,json
from flask import Flask, jsonify, request, make_response
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine,text
from flask_httpauth import HTTPBasicAuth
import uuid,regex
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from google.cloud import pubsub_v1
from datetime import datetime, timedelta

PUBSUB_TOPIC = "verify_email"

logger = logging.getLogger()

app = Flask(__name__)

# Set up structured logging
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        # Add level and time fields
        log_record['level'] = record.levelname
        log_record['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))

# Create logger and add handler
formatter = CustomJsonFormatter()
#json_formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}')

if os.name == 'posix':
    log_dir = '/var/log/webapp'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    json_log_handler = RotatingFileHandler(os.path.join(log_dir, 'requests.log'), maxBytes=10000, backupCount=1)
else:
    json_log_handler = RotatingFileHandler('requests.log', maxBytes=10000, backupCount=1)

json_log_handler.setFormatter(formatter)
# app.logger.info("Testing logging permissions")
logger.addHandler(json_log_handler)
logger.setLevel(logging.INFO)

formatter.default_time_format = '%Y-%m-%dT%H:%M:%SZ'

load_dotenv()

db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']
db_host = os.environ['DB_HOST']

engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/")
with engine.connect() as connection:
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
    connection.execute(text(f"USE {db_name}"))

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
auth = HTTPBasicAuth()


def is_connected():
    try:
        db.session.execute(text('select 1'))
        return True
    except:
        return False

def generate_verification_token():
    verification_token = str(uuid.uuid4())
    return verification_token
class user_data(db.Model):
    __tablename__ = 'user_data'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(29), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    account_created = db.Column(db.DateTime, server_default=db.func.now())
    account_updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), nullable=True)
    mail_sent = db.Column(db.Boolean, default=False, nullable=False)
    mail_sent_time = db.Column(db.DateTime, nullable=True)
    expiration_time = db.Column(db.DateTime, nullable=True)

with app.app_context():
    db.create_all()


@app.route('/healthz', methods=['GET'])
def health_check():
    if request.method != 'GET':
        response = make_response("", 405)
        response.headers['Cache-Control'] = 'no-cache'
        return response
    if request.get_data() or request.args:
        response = make_response("", 400)
        response.headers['Cache-Control'] = 'no-cache'
        return response
    else:
        if is_connected():
            response = make_response("", 200)
        else:
            response = make_response("", 503)
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.errorhandler(405)
def method_not_allowed_error(error):
    response = make_response("", 405)
    response.headers['Cache-Control'] = 'no-cache'
    return response

@auth.error_handler
def unauthorized():
    response = make_response(jsonify({"error": "Authentication failed"}), 401)
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.errorhandler(404)
def method_not_allowed_error(error):
    response = make_response("", 404)
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.errorhandler(400)
def method_not_allowed_error(error):
    response = make_response("", 400)
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.errorhandler(503)
def method_not_allowed_error(error):
    response = make_response("", 503)
    response.headers['Cache-Control'] = 'no-cache'
    return response

@app.errorhandler(500)
def method_not_allowed_error(error):
    response = make_response("", 500)
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/v1/user', methods=['POST'])
def register():
    getuser_data = request.get_json()
    valid_keys = ['username', 'password', 'first_name', 'last_name']
    getuser_data = {key: getuser_data.get(key) for key in valid_keys}
    user_email = getuser_data.get('username')
    user_password = getuser_data.get('password')
    user_firstname = getuser_data.get('first_name')
    user_lastname = getuser_data.get('last_name')
    email_format_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not user_email or not user_password or not user_firstname or not user_lastname:
        response = make_response("", 400)
        return response
    elif not regex.match(email_format_regex, user_email):
        response = make_response("", 400)
        return response

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), salt=salt).decode('utf-8')
    token = generate_verification_token()
    try:
        mail_sent_time = datetime.now()
        expiration_time = mail_sent_time + timedelta(minutes=2)

        new_user = user_data(email=user_email, password_hash=hashed_password, salt=salt,
                             first_name=user_firstname, last_name=user_lastname,verification_token=token,mail_sent_time=mail_sent_time,expiration_time=expiration_time)
        db.session.add(new_user)
        db.session.commit()
        user = user_data.query.filter_by(email=user_email).first()
        user_info = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'account_created': user.account_created,
        'account_updated': user.account_updated
    }
        payload = {
            "user_id": user.id,
            "email": user.email,
            "verification_token": user.verification_token
        }

        payload_json = json.dumps(payload)
        payload_bytes = payload_json.encode('utf-8')

        # Publish message to Pub/Sub topic
        publisher = pubsub_v1.PublisherClient()
        project_id = os.environ.get('PROJECT_ID')
        topic_name = PUBSUB_TOPIC
        topic_path = publisher.topic_path(project_id, topic_name)
        future = publisher.publish(topic_path, data=payload_bytes)
        message_id = future.result()

        print(f"Published message ID: {message_id}")
        response = make_response(jsonify(user_info), 201)
        return response
    # https://stackoverflow.com/questions/24522290/cannot-catch-sqlalchemy-integrityerror
    except IntegrityError as e:
        db.session.rollback()
        print(e)
        response = make_response("", 400)
        return response

@app.route('/v1/user/verify', methods=['GET'])
def verify_user():
    verify_token = request.args.get('verify_token')
    if not verify_token:
        response = make_response("", 400)
        return response

    user = user_data.query.filter_by(verification_token=verify_token).first()
    if not user:
        response = make_response(jsonify({"error": "Invalid verification token"}), 404)
        return response

    if user.mail_sent_time and datetime.now() - user.mail_sent_time > timedelta(minutes=2):
        response = make_response(jsonify({"error": "Mail sent has been expired"}), 400)
        return response

    # Update the user's is_verified status
    user.is_verified = True
    try:
        db.session.commit()
        response = make_response(jsonify({"message": "User verified successfully"}), 200)
        return response
    except IntegrityError as e:
        db.session.rollback()
        print(e)
        response = make_response(jsonify({"error":"Failed to verify user"}), 500)
        return response

@auth.verify_password
def verify_password(username, password):
    user = user_data.query.filter_by(email=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return username


# get user details
@app.route('/v1/user/self', methods=['GET'])
@auth.login_required
def get_user():
    user_email = auth.username()
    user = user_data.query.filter_by(email=user_email).first()

    if not user:
        response = make_response("", 404)
        return response
    
    if not user.is_verified:
        response = make_response(jsonify({"error":"User is not verified, Please verify!"}), 403)
        return response
    
    user_info = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'account_created': user.account_created,
        'account_updated': user.account_updated
    }

    response = make_response(jsonify(user_info), 200)
    return response


# update user details
@app.route('/v1/user/self', methods=['PUT'])
@auth.login_required
def update_user():
    user_email = auth.username()
    user = user_data.query.filter_by(email=user_email).first()

    if not user:
        response = make_response("", 404)
        return response

    if not user.is_verified:
        response = make_response(jsonify({"error":"User is not verified, Please verify!"}), 403)
        return response
    
    update_data = request.get_json()
    valid_keys = ['password', 'first_name', 'last_name']
    are_keys_valid = all(key in valid_keys for key in update_data.keys())
    if are_keys_valid :
        new_first_name = update_data.get('first_name')
        new_last_name = update_data.get('last_name')
        new_password = update_data.get('password')
    else:
        response = make_response("", 400)
        return response

    if not new_first_name or not new_last_name or (new_password and len(new_password) < 6):
        response = make_response("", 400)
        return response

    # Update allowed fields
    user.first_name = new_first_name
    user.last_name = new_last_name

    if new_password:
        user.salt = bcrypt.gensalt()
        user.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt=user.salt).decode('utf-8')

    user.account_updated = db.func.now()

    try:
        db.session.commit()
        response = make_response("", 204)
        return response
    except IntegrityError:
        db.session.rollback()
        response = make_response("", 500)
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=False)
