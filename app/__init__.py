import datetime
from flask import Flask, request, Blueprint, url_for
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
#from flask_user import UserManager, user_sent_invitation, user_registered
from flask_babelex import Babel
from werkzeug.security import generate_password_hash, check_password_hash

from app.utils import make_403
from config import config
from app.api.response import APIResponseFactory
from app.forms.register import CustomRegisterForm
from flask_httpauth import HTTPBasicAuth


# Initialize Flask extensions
db = SQLAlchemy()
mail = Mail()
auth = HTTPBasicAuth()
# Initialize Flask-Babel
babel = Babel()

api_bp = Blueprint('api_bp', __name__, template_folder='templates')
app_bp = Blueprint('app_bp', __name__, template_folder='templates', static_folder='static')


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)




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
    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=app.config["APP_URL_PREFIX"])

    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    app.scss = Scss(app)
    babel.init_app(app)

    CORS(app, supports_credentials=True, resources={r"*": {"origins": "*"}})


    # Use the browser's language preferences to select an available translation
    @babel.localeselector
    def get_locale():
        translations = [str(translation) for translation in babel.list_translations()]
        return request.accept_languages.best_match(translations)

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
        return user["username"]

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

    from app import routes
    from app.api import routes as api_routes

    #app_bp.url_prefix = app.config["APP_URL_PREFIX"]
    #api_bp.url_prefix = app.config["APP_URL_PREFIX"]

    app.register_blueprint(app_bp)
    app.register_blueprint(api_bp)

    return app
