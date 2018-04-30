from flask import request
from sqlalchemy.orm.exc import NoResultFound

from app import get_current_user, auth, db
from app.api.response import APIResponseFactory
from app.api.routes import api_bp
from app.models import User, Role

"""
===========================
    Users
===========================
"""


@api_bp.route('/api/<api_version>/user')
def api_current_user(api_version):
    # TODO: change hard coded id
    try:
        user = get_current_user()
        if user is None:
            response = APIResponseFactory.make_response()
        else:
            response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "User not found"
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/<user_id>')
@auth.login_required
def api_users(api_version, user_id):
    response = None
    user = get_current_user()

    if (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        try:
            target_user = User.query.filter(User.id == user_id).one()
            response = APIResponseFactory.make_response(data=target_user.serialize())
        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "User {0} not found".format(user_id)
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/<user_id>/roles')
@auth.login_required
def api_users_roles(api_version, user_id):
    response = None
    user = get_current_user()

    if user is not None:
        if (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
    if response is None:
        try:
            target_user = User.query.filter(User.id == user_id).one()
            response = APIResponseFactory.make_response(data=[r.serialize() for r in target_user.roles])
        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "User {0} not found".format(user_id)
            })

    return APIResponseFactory.jsonify(response)


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
    response = None
    user = get_current_user()

    if (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:

        data = request.get_json()

        if "data" in data:
            data = data["data"]
            if not isinstance(data, list):
                data = [data]

            target_user = User.query.filter(User.id == user_id).one()

            for role_name in [r["name"] for r in data]:

                if not target_user.has_role(role_name):
                    if role_name == "admin" and not user.is_admin:
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Access forbidden"
                        })
                        break
                    else:
                        role = Role.query.filter(Role.name == role_name).one()
                        target_user.roles.append(role)

            if response is None:
                db.session.add(target_user)

                try:
                    db.session.commit()
                    response = APIResponseFactory.make_response(data=[r.serialize() for r in target_user.roles])
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot insert data", "details": str(e)
                    })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/<user_id>', methods=['DELETE'])
@auth.login_required
def api_delete_users(api_version, user_id):
    response = None
    user = get_current_user()
    if not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            target_user = User.query.filter(User.id == user_id).one()

            if target_user.is_admin and not user.is_admin:
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Access forbidden"
                })

            if response is None:
                db.session.delete(target_user)

            try:
                db.session.commit()
                response = APIResponseFactory.make_response(data=[])
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot delete data", "details": str(e)
                })

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "User {0} not found".format(user_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/<user_id>/roles', methods=['DELETE'])
@auth.login_required
def api_delete_users_roles(api_version, user_id):
    response = None
    user = get_current_user()
    if not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            target_user = User.query.filter(User.id == user_id).one()

            if target_user.is_admin and not user.is_admin:
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Access forbidden"
                })

            if response is None:
                target_user.roles = [Role.query.filter(Role.name == "student").one()]
                db.session.add(target_user)

            try:
                db.session.commit()
                response = APIResponseFactory.make_response(data=[])
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot delete data", "details": str(e)
                })

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "User {0} not found".format(user_id)
            })
    return APIResponseFactory.jsonify(response)