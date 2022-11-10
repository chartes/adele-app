from functools import wraps

from flask import current_app

"""
========================================================
    A bunch of useful functions
========================================================
"""
def check_no_XMLParserError(content):
    if content is not None and "parsererror" in content:
        print("PARSER_ERROR", content)
        return make_400(details='Parser Error: %s' % content)

def get_user_from_username(username):
    from app import models
    return models.User.query.filter(models.User.username == username).first()


def get_current_user():
    from app.models import AnonymousUser, User
    from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request_optional

    try:
        verify_jwt_in_request_optional()
    except Exception as e:
        print(e)
        return AnonymousUser()

    identity = get_jwt_identity()
    if identity is None:
        user = AnonymousUser()
    else:
        user = User.query.filter(User.email == identity).first()
        if user is None:
            user = AnonymousUser()

    return user


def make_error(status, title, details=None):
    from app import APIResponseFactory
    e = {"status": status, "title": title}
    if details:
        e["details"] = details
    return APIResponseFactory.make_response(status=status, errors=e)


def make_success(data, status=200):
    from app import APIResponseFactory
    return APIResponseFactory.make_response(status=status, data=data)


def make_403(details=None):
    return make_error(403, "Access forbidden", details)


def make_404(details=None):
    return make_error(404, "The resource does not exist", details)


def make_400(details=None):
    return make_error(400, "Error", details)


def make_401(details=None):
    return make_error(401, "Error", details)


def make_409(details=None):
    return make_error(409, "Conflict with the current state of the target resource", details)


def make_200(data=None):
    if data is None:
        data = []
    return make_success(data)


def make_204():
    return make_success(data={}, status=204)

def make_201(data):
    return make_success(data, status=201)

def forbid_if_not_in_whitelist(app, doc):
    user = app.get_current_user()
    if doc.whitelist is not None:
        if doc.user_id == user.id or user in doc.whitelist.users or user.is_admin:
            return None
        else:
            return make_403(details="Your are not allowed to modify this document")


def forbid_if_nor_teacher_nor_admin_and_wants_user_data(app, wanted_user_id):
    user = app.get_current_user()
    # if anonymous or mere student wants to read data of another student
    if user.is_anonymous or not (user.is_teacher or user.is_admin) and wanted_user_id is not None and int(wanted_user_id) != int(user.id):
        msg = "You must be a teacher or an admin"
        return make_403(details=msg)
    else:
        return None


def forbid_if_other_user(app, wanted_user_id):
    user = app.get_current_user()
    # if anonymous or mere student wants to read data of another student
    if user.is_anonymous or wanted_user_id is not None and int(wanted_user_id) != int(user.id):
        return make_403(details="Wrong user")
    else:
        return None


def forbid_if_nor_teacher_nor_admin(view_function):
    @wraps(view_function)
    def wrapped_f(*args, **kwargs):
        user = current_app.get_current_user()
        if user.is_anonymous or not (user.is_teacher or user.is_admin):
            msg = "This resource is only available to teachers and admins"
            print(msg)
            return make_403(details=msg)
        return view_function(*args, **kwargs)
    return wrapped_f


def forbid_if_not_admin(view_function):
    @wraps(view_function)
    def wrapped_f(*args, **kwargs):
        user = current_app.get_current_user()
        if user.is_anonymous or not user.is_admin:
            msg = "This resource is only available to teachers and admins"
            print(msg)
            return make_403(details=msg)
        return view_function(*args, **kwargs)

    return wrapped_f

def get_doc(doc_id):
    from app.models import Document
    return Document.query.filter(Document.id == doc_id).first()

def is_closed(doc_id):
    from app.models import Document
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()
    if doc.is_closed:
        print("doc", doc.id, "is closed")
        return make_403()


def forbid_if_validation_step(doc_id, gte):
    from app.models import Document
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc and doc.validation_step >= gte:
        print("Validation step error:", doc.validation_step, ">=", gte)
        return make_403(details="Validation step")
