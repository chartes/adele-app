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


def make_error(status, title, details=None):
    from app import APIResponseFactory
    e = {"status": status, "title": title,}
    if details:
        e["details"] = details
    return APIResponseFactory.make_response(status=status, errors=e)


def make_success(data):
    from app import APIResponseFactory
    return APIResponseFactory.make_response(status=200, data=data)


def make_403(details=None):
    return make_error(403, "Access forbidden", details)


def make_404(details=None):
    return make_error(404, "The resource does not exist", details)


def make_409(details=None):
    return make_error(409, "Conflict with the current state of the target resource", details)


def make_200(data=[]):
    return make_success(data)


def forbid_if_nor_teacher_nor_admin(app):
    user = app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        return False, make_403("This resource is only accessible to teachers and admins")
    else:
        return True, None


def forbid_if_nor_teacher_nor_admin(app):
    user = app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        return make_403("This resource is only accessible to teachers and admins")
    else:
        return None


def forbid_if_nor_teacher_nor_admin_and_wants_user_data(app, wanted_user_id):
    user = app.get_current_user()
    # if anonymous or mere student wants to read data of another student
    if user.is_anonymous or not (user.is_teacher or user.is_admin) and wanted_user_id is not None and int(wanted_user_id) != int(user.id):
        return make_403("You must be a teacher or an admin")
    else:
        return None


