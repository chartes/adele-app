from flask_user.forms import RegisterForm
from wtforms import StringField
from wtforms.validators import DataRequired


class CustomRegisterForm(RegisterForm):
    first_name = StringField('First name', validators=[DataRequired('First name is required')])
    last_name = StringField('Last name',  validators=[DataRequired('Last name is required')])
