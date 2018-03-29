from flask import Flask
from flask_mail import Mail
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter
from flask_user.forms import RegisterForm
from wtforms import StringField
from wtforms.validators import DataRequired

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask extensions
db = SQLAlchemy(app)  # Initialize Flask-SQLAlchemy
mail = Mail(app)  # Initialize Flask-Mail
scss = Scss(app)



from app import routes, models


"""
---------------------------------
Setup Flask-User
---------------------------------
"""

# Register the User model
db_adapter = SQLAlchemyAdapter(db, models.User)

from werkzeug.security import generate_password_hash, check_password_hash

class CustomUserManager(UserManager):
    def hash_password(self, password):
        #print(generate_password_hash(password.encode('utf-8')))
        return generate_password_hash(password.encode('utf-8'))

    def verify_password(self, password, user):
        print(self.hash_password(password), self.get_password(user))
        return check_password_hash(self.get_password(user), password)

class MyRegisterForm(RegisterForm):
    first_name = StringField('First name', validators=[DataRequired('First name is required')])
    last_name  = StringField('Last name',  validators=[DataRequired('Last name is required')])


# Initialize Flask-User
user_manager = CustomUserManager(db_adapter, app, register_form=MyRegisterForm)
