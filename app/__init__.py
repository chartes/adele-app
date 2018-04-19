import pprint

import flask_login
from flask import Flask, url_for, redirect
from flask_login import current_user
from flask_mail import Mail
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from werkzeug.security import generate_password_hash, check_password_hash

from app.api.response import APIResponseFactory
from app.forms.register import CustomRegisterForm


from  flask_httpauth import HTTPBasicAuth


from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask extensions
db = SQLAlchemy(app)  # Initialize Flask-SQLAlchemy
mail = Mail(app)  # Initialize Flask-Mail
scss = Scss(app)
auth = HTTPBasicAuth()


from app import models


def get_user_from_username(username):
    return models.User.query.filter(models.User.username == username).first()


def get_current_user():
    if auth.username() == "":
        if current_user.is_anonymous:
            user = None
        else:
            user = current_user
    else:
        user = models.User.query.filter(models.User.username == auth.username()).one()
    return user

def role_required(*wanted_roles):
    """
    Ensure the logged user has all of the wanted roles
    """
    def wrap(route):

        def func_wrapper(*args, **kargs):
            user = get_current_user()
            if user is None:
                return redirect("/")

            for role in wanted_roles:
                if not user.has_role(role):
                    response = APIResponseFactory.make_response(
                        errors={"status": 401, "title": "You are not authorized to access this resource"}
                    )
                    return APIResponseFactory.jsonify(response)
            # roles are OK
            return route(*args, **kargs)
        return func_wrapper
    return wrap


"""
---------------------------------
Setup Flask-User
---------------------------------
"""

# Register the User model
db_adapter = SQLAlchemyAdapter(db, models.User)


class CustomUserManager(UserManager):
    def hash_password(self, password):
        return generate_password_hash(password.encode('utf-8'))

    def verify_password(self, password, user):
        return check_password_hash(self.get_password(user), password)


# Initialize Flask-User
user_manager = CustomUserManager(db_adapter, app, register_form=CustomRegisterForm)


# Initialize the HTTP Auth mechanism
@auth.verify_password
def verify_password(username, password):
    user = models.User.query.filter(models.User.username == username).first()
    if not user:
        return False
    return user_manager.verify_password(password, user)


from app import routes
