

from flask import Flask, request
from flask_mail import Mail
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from flask_babelex import Babel
from werkzeug.security import generate_password_hash, check_password_hash

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


def create_app(config_name="dev"):
    """ Create the application """
    app = Flask( __name__)
    if not isinstance(config_name, str):
        app.config.from_object(config)
    else:
        app.config.from_object(config[config_name])

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    app.scss = Scss(app)
    babel.init_app(app)

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

    # Register the User model
    # db_adapter = SQLAlchemyAdapter(db, models.User)
    # Initialize Flask-User
    user_manager = CustomUserManager(app, db, models.User)

    @auth.verify_password
    def verify_password(username_or_token, password):
        user = models.User.verify_auth_token(username_or_token)
        if not user:
            user = models.User.query.filter(models.User.username == username_or_token).first()
            if not user or not verify_password(password, user.password):
                return False
        return True

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
        Import all routes
    ========================================================
    """

    from app import routes
    from app.api import routes as api_routes

    app.register_blueprint(routes.app_bp)
    app.register_blueprint(api_routes.api_bp)

    return app