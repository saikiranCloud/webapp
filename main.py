import os
from flask import Flask, jsonify, request, make_response
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine,text
from flask_httpauth import HTTPBasicAuth
import uuid,regex


app = Flask(__name__)
load_dotenv()

db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']


engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@localhost/")
with engine.connect() as connection:
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
    connection.execute(text(f"USE {db_name}"))

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@localhost/{db_name}"
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


with app.app_context():
    db.create_all()


@app.route('/healthz', methods=['GET'])
def health_check():
    if request.method != 'GET':
        response = make_response("", 405)
        response.headers['Cache-Control'] = 'no-cache'
        return response
    if request.get_data():
        response = make_response("", 404)
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

@app.errorhandler(401)
def unauthorized_error(error):
    response = make_response("",401)
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

    try:
        new_user = user_data(email=user_email, password_hash=hashed_password, salt=salt,
                             first_name=user_firstname, last_name=user_lastname)
        db.session.add(new_user)
        db.session.commit()
        user = user_data.query.filter_by(email=user_email).first()
        user_info = {
        'id': user.id,
        'username': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'account_created': user.account_created,
        'account_updated': user.account_updated
    }

        response = make_response(jsonify(user_info), 201)
        return response
    # https://stackoverflow.com/questions/24522290/cannot-catch-sqlalchemy-integrityerror
    except IntegrityError as e:
        db.session.rollback()
        print(e)
        response = make_response("", 400)
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

    user_info = {
        'id': user.id,
        'username': user.email,
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

    update_data = request.get_json()
    new_first_name = update_data.get('first_name')
    new_last_name = update_data.get('last_name')
    new_password = update_data.get('password')

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
        response = make_response("", 200)
        return response
    except IntegrityError:
        db.session.rollback()
        response = make_response("", 500)
        return response

if __name__ == '__main__':
    app.run(debug=True)
