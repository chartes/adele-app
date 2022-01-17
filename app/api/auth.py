import datetime
import string
from random import randint, random, choice

from flask import jsonify, request, url_for, app, current_app
from flask_jwt_extended import create_access_token, set_access_cookies, \
    unset_jwt_cookies, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, set_refresh_cookies, \
    jwt_required, unset_refresh_cookies, unset_access_cookies
from flask_mail import Message
import jwt
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from app import api_bp, make_403, db, mail
from app.models import User, Role

from app.utils import make_401, forbid_if_nor_teacher_nor_admin, make_400, make_200


def refresh_token(user, resp=None):
    if not user.is_anonymous:
        access_token = create_access_token(identity=user.to_json(), fresh=True)
        auth_headers = {'login': True, 'user-adele': ''}
        if resp:
            resp.headers["login"] = auth_headers["login"]
            resp.headers["user-adele"] = auth_headers["user-adele"]
        else:
            resp = jsonify(auth_headers)
        set_access_cookies(resp, access_token)
        print("token refreshed")
    else:
        auth_headers = {'logout': True, 'user-adele': None}
        if resp:
            resp.headers["logout"] = auth_headers["logout"]
            resp.headers["user-adele"] = auth_headers["user-adele"]
        else:
            resp = jsonify(auth_headers)
        unset_jwt_cookies(resp)
        print("token cleared")
    return resp, 200


@api_bp.route('/api/<api_version>/logout')
def logout(api_version):
    resp = jsonify({})
    unset_access_cookies(resp)
    unset_refresh_cookies(resp)
    return resp, 200

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

    token = jwt.encode({
        'sub': user.username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60*24)},
        current_app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8'), 'user_data': user.serialize()})


@api_bp.route('/api/<api_version>/invite-user', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def invite_user(api_version):
    json = request.get_json(force=True)

    email = json.get('email', None)
    role = json.get('role', 'student')

    if email is None:
        print("Email unknown")
        return make_401("Email unknown")

    username = email.split('@')[0]
    password = ''.join(choice(string.ascii_letters) for i in range(5)) + str(randint(1, 100)).zfill(3)

    msg = Message('Contribute to Adele', sender=current_app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = "Vous avez été invité(e) à contribuer au projet Adele (" \
               "https://dev.chartes.psl.eu/adele/profile).\nIdentifiant: %s\nMot de passe: %s\nN'oubliez pas de " \
               "changer votre mot de passe après votre première connexion !" % (email, password)

    print(email, role)
    print(msg.body)

    try:
        new_user = User(username=username, password=generate_password_hash(password), email=email,
                        first_name=username, last_name=username,
                        active=True, email_confirmed_at=datetime.datetime.now())

        print('checkpassword:', check_password_hash(new_user.password, password))

        if role not in ('student', 'teacher', 'admin'):
            role = 'student'

        if role == 'admin':
            new_user.roles = Role.query.filter(Role.id >= 1).all()
        elif role == 'student':
            new_user.roles = Role.query.filter(Role.id == 2).all()
        elif role == 'teacher':
            new_user.roles = Role.query.filter(Role.id >= 2).all()

        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        print(f'cannot invite user ({username}, {email}): {str(e)}')
        db.session.rollback()
        return make_400("Cannot invite user: %s" % str(e))

    mail.send(msg)
    return make_200(msg)


@api_bp.route('/api/<api_version>/update-user', methods=['POST'])
@jwt_required
def update_user(api_version):
    json = request.get_json(force=True)

    firstname = json.get('firstname', None)
    lastname = json.get('lastname', None)
    email = json.get('email', None)
    username = json.get('username', None)
    password = json.get('password', None)
    password2 = json.get('password2', None)

    user = User.query.filter(User.email == email).first()
    print("trying to log in as", user)

    if user is None:
        print("User unknown")
        return make_401("User unknown")

    if password != password2:
        print("Passwords do not match")
        return make_401("Invalid credentials")

    # passwords_match = check_password_hash(user.password, password)

    try:
        print('update info:', username, firstname, lastname, email)
        user.password = generate_password_hash(password)
        user.username = username if username else user.username
        user.first_name = firstname if firstname else user.first_name
        user.last_name = lastname if lastname else user.last_name
        user.email = email if email else user.email
        print('update user to', user.serialize())

        db.session.add(user)
        db.session.commit()

        resp = {"error": None}
    except Exception as e:
        resp = {"error": str(e)}

    resp.update(user.serialize())
    resp = jsonify(resp)

    return resp, 200
