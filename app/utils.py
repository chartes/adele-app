from flask_login import current_user
from app import auth, models


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
        user = models.User.query.filter(models.User.username == auth.username()).first()
    return user