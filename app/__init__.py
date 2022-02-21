import datetime
import uuid

from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from app.utils import make_403
from config import config
from app.api.response import APIResponseFactory
from flask_httpauth import HTTPBasicAuth

# Initialize Flask extensions
mail = Mail()
auth = HTTPBasicAuth()

api_bp = Blueprint('api_bp', __name__)


def auto_constraint_name(constraint, table):
    if constraint.name is None or constraint.name == "_unnamed_":
        return "sa_autoname_%s" % str(uuid.uuid4())[0:5]
    else:
        return constraint.name

naming_convention = {
    "auto_constraint_name": auto_constraint_name,
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    "ck": "ck_%(table_name)s_%(auto_constraint_name)s",
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

from sqlalchemy.engine import Engine
from sqlalchemy import event
from flask_cors import CORS

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

"""
=========================================================
    Override default 401 Reponse with a 403 Response 
========================================================
"""


auth.auth_error_callback = make_403


def create_app(config_name="dev"):
    """ Create the application """
    app = Flask( __name__)
    if not isinstance(config_name, str):
        app.config.from_object(config)
    else:
        app.config.from_object(config[config_name])

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    config[config_name].init_app(app)

    def with_url_prefix(url):
        from flask import request
        return "".join((request.host_url[:-1],  url))

    app.with_url_prefix = with_url_prefix

    db.init_app(app)
    mail.init_app(app)

    CORS(app, supports_credentials=True, resources={r"*": {"origins": "*"}})

    """
    ========================================================
        Import models
    ========================================================
    """

    from app import models

    """
       ========================================================
           Setup Flask-JWT-Extended
       ========================================================
       """
    app.jwt = JWTManager(app)

    # Create a function that will be called whenever create_access_token
    # is used. It will take whatever object is passed into the
    # create_access_token method, and lets us define what custom claims
    # should be added to the access token.
    @app.jwt.user_claims_loader
    def add_claims_to_access_token(user):
        return user["roles"]

    # Create a function that will be called whenever create_access_token
    # is used. It will take whatever object is passed into the
    # create_access_token method, and lets us define what the identity
    # of the access token should be.
    @app.jwt.user_identity_loader
    def user_identity_lookup(user):
        return user["email"]

    """
    ========================================================
        Import utils
    ========================================================
    """
    from app.utils import get_user_from_username, get_current_user

    app.get_current_user = get_current_user
    app.get_user_from_username = get_user_from_username

    """
    ========================================================
        Setup custom filters
    ========================================================
    """

    def format_datetime(value):
        if value:
            d = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            return datetime.datetime.strftime(d, '%d/%m/%Y')
        else:
            return ""

    app.jinja_env.filters['date'] = format_datetime

    """
    ========================================================
        Import all routes
    ========================================================
    """

    from app.api import routes as api_routes
    app.register_blueprint(api_bp)

    return app
