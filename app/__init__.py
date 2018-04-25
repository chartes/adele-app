import pprint
from collections import OrderedDict

from flask import Flask, redirect, url_for
from flask_login import current_user
from flask_mail import Mail
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from sqlalchemy.orm.exc import NoResultFound
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


"""
=========================================================
    Override default 401 Reponse with a 403 Response 
========================================================
"""


def make_json_unauthorized_response():
    resp = APIResponseFactory.jsonify(APIResponseFactory.make_response(errors={
        "status": 403, "title": "Access forbidden"
    }))
    resp.status_code = 200
    return resp


auth.auth_error_callback = make_json_unauthorized_response


"""
========================================================
    Import models
========================================================
"""

from app import models


"""
========================================================
    A bunch of useful functions
========================================================
"""


def get_user_from_username(username):
    return models.User.query.filter(models.User.username == username).first()


def get_current_user():
    if auth.username() == "":
        if current_user.is_anonymous:
            user = None
        else:
            user = current_user
    else:
        try:
            user = models.User.query.filter(models.User.username == auth.username()).one()
        except NoResultFound:
            user = None
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
========================================================
    Setup Flask-User
========================================================
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


"""
========================================================
    Import all routes
========================================================
"""

from app import routes


# OUTPUT A LIST OF ALL ROUTES to API_ROUTES.md

api_rules = {}
for rule in app.url_map.iter_rules():
    if rule.rule.startswith("/api/"):
        if rule.rule in api_rules:
            api_rules[rule.rule].update(rule.methods)
        else:
            api_rules[rule.rule] = set(rule.methods)


with open("API_ROUTES.md", "w") as f:
    for api_rule in sorted(api_rules):
        f.write("{0} {1}\n".format(api_rule, api_rules[api_rule]))