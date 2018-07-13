from flask_login import current_user
from app import auth, models
from app.models import AnonymousUser

"""
========================================================
    A bunch of useful functions
========================================================
"""


def get_user_from_username(username):
    return models.User.query.filter(models.User.username == username).first()


def get_current_user():
    if auth.username() == "":
        user = current_user
        if user.is_anonymous:
            user = AnonymousUser()
    else:
        user = models.User.verify_auth_token(auth.username())
        if not user:
            user = models.User.query.filter(models.User.username == auth.username()).first()
        if not user:
            user = AnonymousUser()

    return user
