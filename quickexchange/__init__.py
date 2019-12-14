import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile("config.py")
db = SQLAlchemy(app)
cors = CORS(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"  # <-- function name of our login route
login_manager.login_message_category = "info"

# Import here to avoid circular imports
from quickexchange import routes


@app.before_first_request
def create_tables():
    if not os.path.exists(app.config["FILE_UPLOAD_PATH"]):
        os.makedirs(app.config["FILE_UPLOAD_PATH"])
    db.create_all()


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

