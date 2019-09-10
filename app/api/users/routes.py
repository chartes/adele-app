from flask import request, current_app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from app import auth, db
from app.api.response import APIResponseFactory
from app.api.routes import api_bp
from app.models import User, Role, Whitelist, Document
from app.utils import make_200, make_404, forbid_if_nor_teacher_nor_admin, make_409, make_403

"""
===========================
    Users
===========================
"""


@api_bp.route('/api/<api_version>/token')
@auth.login_required
def get_auth_token(api_version):
    user = current_app.get_current_user()
    token = user.generate_auth_token()
    return make_200(data=[{'token': token.decode('ascii')}])


@api_bp.route('/api/<api_version>/user')
@auth.login_required
def api_current_user(api_version):
    user = current_app.get_current_user()
    return make_200(data=[user.serialize()])


@api_bp.route('/api/<api_version>/users/<user_id>')
@auth.login_required
def api_users(api_version, user_id):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        target_user = User.query.filter(User.id == user_id).one()
        return make_200(data=[target_user.serialize()])
    except NoResultFound:
        return make_404()


@api_bp.route('/api/<api_version>/users/<user_id>/roles')
@auth.login_required
def api_users_roles(api_version, user_id):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        target_user = User.query.filter(User.id == user_id).one()
        return make_200(data=[r.serialize() for r in target_user.roles])
    except NoResultFound:
        return make_404()

@api_bp.route('/api/<api_version>/users/<user_id>/roles', methods=['POST'])
@auth.login_required
def api_post_users_roles(api_version, user_id):
    """
    {
        "data": [
            {
                "name": "admin"
            },
            {
                "name": "teacher"
            }
        ]
    }
    :param api_version:
    :param user_id:
    :return:
    """

    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    data = request.get_json()
    if "data" in data:
        data = data["data"]

        user = current_app.get_current_user()
        target_user = User.query.filter(User.id == user_id).first()

        for role_name in [r.get("name", None) for r in data]:

            if not target_user.has_roles([role_name]):
                if role_name == "admin" and not user.is_admin:
                    return make_403()
                else:
                    role = Role.query.filter(Role.name == role_name).first()
                    if role:
                        target_user.roles.append(role)

        db.session.add(target_user)
        try:
            db.session.commit()
            return make_200(data=[r.serialize() for r in target_user.roles])
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return make_409()
    else:
        return make_409()


@api_bp.route('/api/<api_version>/users/<user_id>', methods=['DELETE'])
@auth.login_required
def api_delete_user(api_version, user_id):

    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        target_user = User.query.filter(User.id == user_id).one()
        user = current_app.get_current_user()

        if target_user.is_admin and not user.is_admin:
            return make_403()

        try:
            db.session.delete(target_user)
            db.session.commit()
            return make_200(data=[])
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return make_409()

    except NoResultFound:
        return make_404()


@api_bp.route('/api/<api_version>/users/<user_id>/roles', methods=['DELETE'])
@auth.login_required
def api_delete_users_roles(api_version, user_id):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        target_user = User.query.filter(User.id == user_id).one()
    except NoResultFound:
        return make_404()

    user = current_app.get_current_user()
    if target_user.is_admin and not user.is_admin:
        return make_403()

    target_user.roles = [Role.query.filter(Role.name == "student").first()]
    db.session.add(target_user)

    try:
        db.session.commit()
        return make_200()
    except Exception as e:
        db.session.rollback()
        return make_409()


@api_bp.route('/api/<api_version>/whitelists/<whitelist_id>/add-users', methods=['POST'])
@auth.login_required
def add_user_to_whitelist(api_version, whitelist_id):
    """
    {
        data: {
            user_id : [1, 2]
        }
    }
    :return:
    """
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    data = request.get_json()
    data = data["data"]
    user_ids = data.get("user_id") or []

    whitelist = Whitelist.query.filter(Whitelist.id == whitelist_id).first()
    users = User.query.filter(User.id.in_(user_ids)).all()
    # make sure you don't twice a same user
    whitelist.users.extend([u for u in users if u.id not in [u.id for u in whitelist.users]])

    try:
        db.session.commit()
        return make_200(data=[{
            "users": [u.serialize() for u in whitelist.users],
            "whitelist": whitelist.serialize()
        }])
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_409()


@api_bp.route('/api/<api_version>/whitelists/<whitelist_id>/remove-user/<user_id>', methods=['DELETE'])
@auth.login_required
def remove_user_from_whitelist(api_version, whitelist_id, user_id):
    """
    :return:
    """
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    whitelist = Whitelist.query.filter(Whitelist.id == whitelist_id).first()
    user = User.query.filter(User.id == user_id).first()

    # remove the user from the whitelist
    whitelist.users = [u for u in whitelist.users if u.id != int(user.id)]

    try:
        db.session.commit()
        return make_200()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_409()


@api_bp.route('/api/<api_version>/whitelists/<whitelist_id>')
@auth.login_required
def api_get_whitelist(api_version, whitelist_id):

    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    w = Whitelist.query.filter(Whitelist.id == whitelist_id).first()
    if w is None:
        return make_404()
    else:
        return make_200(data=[w.serialize()])


@api_bp.route('/api/<api_version>/whitelists', methods=['POST'])
@auth.login_required
def api_post_whitelist(api_version):
    """
    {
        data: [{
            whitelist_name : 'My new whitelist'
        }]
    }
    :return:
    """
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    data = request.get_json()

    try:
        wls = []
        for d in data["data"]:
            new_whitelist_name = d.get("whitelist_name")
            whitelist = Whitelist(label=new_whitelist_name)
            db.session.add(whitelist)
            wls.append(whitelist)
            db.session.flush()
        db.session.commit()
        return make_200(data=[w.serialize() for w in wls])
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_409()


@api_bp.route('/api/<api_version>/whitelists/<whitelist_id>', methods=['DELETE'])
@auth.login_required
def delete_whitelist(api_version, whitelist_id):
    """
    :return:
    """
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        whitelist = Whitelist.query.filter(Whitelist.id == whitelist_id).one()
        # unbind the associated documents
        associated_docs = Document.query.filter(Document.whitelist_id == whitelist.id).all()
        for doc in associated_docs:
            doc.whitelist_id = None
        # then delete the whitelist
        db.session.delete(whitelist)
        db.session.commit()
        return make_200()
    except NoResultFound as e:
        db.session.rollback()
        print(str(e))
        return make_404()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_409()

