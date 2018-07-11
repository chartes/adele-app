from flask_user.forms import RegisterForm
from wtforms import StringField


class CustomRegisterForm(RegisterForm):
    first_name = StringField('First name')
    last_name = StringField('Last name')
