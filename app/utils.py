from flask_login import current_user

"""
========================================================
    A bunch of useful functions
========================================================
"""


def get_user_from_username(username):
    from app import models
    return models.User.query.filter(models.User.username == username).first()


def get_current_user():
    from app import auth, models
    from app.models import AnonymousUser
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


def make_403():
    from app import APIResponseFactory
    return APIResponseFactory.make_response(status=403, errors={
        "status": 403, "title": "Access forbidden"
    })


def forbid_if_nor_teacher_nor_admin(app):
    user = app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        return False, make_403()
    else:
        return True, None
