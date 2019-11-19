import datetime
from flask import Flask, request, Blueprint, url_for
from flask_mail import Mail
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, user_sent_invitation, user_registered
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

    CORS(app, resources={r"*": {"origins": "*"}})


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
        Setup Flask-User
    ========================================================
    """
    class CustomUserManager(UserManager):
        def customize(self, app):
            self.RegisterFormClass = CustomRegisterForm
            self.UserInvitationClass = models.UserInvitation
            self.email_manager._render_and_send_email_with_exceptions = self.email_manager._render_and_send_email

            def with_protection(*args, **kargs):
                try:
                    self.email_manager._render_and_send_email_with_exceptions(*args, **kargs)
                except Exception as e:
                    print(e)
            self.email_manager._render_and_send_email = with_protection

        def hash_password(self, password):
            return generate_password_hash(password.encode('utf-8'))

        def verify_password(self, password, password_hash):
            return check_password_hash(password_hash, password)

        def _endpoint_url(self, endpoint):
            return url_for(endpoint) if endpoint else url_for('app_bp.index')

    # Initialize Flask-User
    user_manager = CustomUserManager(app, db,
                                     UserClass=models.User,
                                     UserInvitationClass=models.UserInvitation)

    @auth.verify_password
    def verify_password(username_or_token, password):
        user = models.User.verify_auth_token(username_or_token)
        if not user:
            user = models.User.query.filter(models.User.username == username_or_token).first()
            if not user or not user_manager.verify_password(password, user.password):
                return False
        return True

    @user_registered.connect_via(app)
    def after_registered_hook(sender, user, user_invitation):
        print("USER %s REGISTERED" % user.serialize())
        default_role = models.Role.query.filter(models.Role.name == 'student').first()
        user.roles.append(default_role)
        db.session.commit()
        print("USER %s gains '%s' role " % (user.serialize(), default_role.serialize()))


    @user_sent_invitation.connect_via(app)
    def after_invitation_hook(sender, **extra):
        print("USER SENT INVITATION: ", extra)

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
