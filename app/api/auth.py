from flask import jsonify,  request, url_for
from flask_jwt_extended import create_access_token, set_access_cookies, \
    unset_jwt_cookies, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, set_refresh_cookies
from sqlalchemy import or_
from werkzeug.security import check_password_hash

from app import api_bp, make_403
from app.models import User

from app.utils import make_401


def refresh_token(user, resp=None):
    if not user.is_anonymous:
        access_token = create_access_token(identity=user.to_json(), fresh=True)
        auth_headers = {'login': True, 'user': ''}
        if resp:
            resp.headers["login"] = auth_headers["login"]
            resp.headers["user"] = auth_headers["user"]
        else:
            resp = jsonify(auth_headers)
        set_access_cookies(resp, access_token)
        print("token refreshed")
    else:
        auth_headers = {'logout': True, 'user': None}
        if resp:
            resp.headers["logout"] = auth_headers["logout"]
            resp.headers["user"] = auth_headers["user"]
        else:
            resp = jsonify(auth_headers)
        unset_jwt_cookies(resp)
        print("token cleared")
    return resp, 200


def create_tokens(user):
    u = user.serialize()
    access_token = create_access_token(identity=u, fresh=True)
    refresh_token = create_refresh_token(u)
    data = {
        'username': user.username,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'id': user.id,
        'email': user.email,
        'roles': [r.name for r in user.roles]
    }
    return data, access_token, refresh_token,


@api_bp.route('/api/<api_version>/login', methods=['POST'])
def login(api_version):

    json = request.get_json(force=True)
    username = json.get('email', None)
    password = json.get('password', None)
    user = User.query.filter(or_(User.username == username, User.email == username)).first()
    print("trying to log in as", user)

    if user is None:
        print("User unknown")
        return make_401("User unknown")

    passwords_match = check_password_hash(user.password, password)
    if not passwords_match:
        print("Invalid credentials")
        return make_401("Invalid credentials")

    data, access_token, refresh_token = create_tokens(user)

    resp = jsonify(data)

    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    return resp, 200


@api_bp.route('/api/<api_version>/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh(api_version):
    user = get_jwt_identity()
    user = User.query.filter(User.username == user).first()
    if user is None:
        return make_403("User not found")

    data, access_token, refresh_token = create_tokens(user)

    resp = jsonify(data)
    set_access_cookies(resp, access_token)
    print("token refreshed")

    return resp, 200


