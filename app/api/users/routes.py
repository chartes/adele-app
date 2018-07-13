from flask import request, current_app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from app import auth, db
from app.api.response import APIResponseFactory
from app.api.routes import api_bp
from app.models import User, Role, Whitelist, Document

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
    return APIResponseFactory.jsonify({'token': token.decode('ascii')})


@api_bp.route('/api/<api_version>/user')
def api_current_user(api_version):
    user = current_app.get_current_user()
    if user.is_anonymous:
        response = APIResponseFactory.make_response()
    else:
        response = APIResponseFactory.make_response(data=user.serialize())

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/<user_id>')
@auth.login_required
def api_users(api_version, user_id):
    response = None
    user = current_app.get_current_user()

    if user.is_anonymous or ((not user.is_teacher and not user.is_admin) and int(user_id) != user.id):
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
    user = current_app.get_current_user()

    if user.is_anonymous or ((not user.is_teacher and not user.is_admin) and int(user_id) != user.id):
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
    user = current_app.get_current_user()

    if user.is_anonymous or ((not user.is_teacher and not user.is_admin) and int(user_id) != user.id):
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
def api_delete_user(api_version, user_id):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or (not user.is_teacher and not user.is_admin):
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
    user = current_app.get_current_user()
    if user.is_anonymous or (not user.is_teacher and not user.is_admin):
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


@api_bp.route('/api/<api_version>/users/add-to-whitelist', methods=['POST'])
@auth.login_required
def add_user_to_whitelist(api_version):
    """
    {
        data: {
            emails : ['aa@bb.fr', 'aaabbbi@.fr'],
            whitelist_id : 1
        }
    }
    :return:
    """
    user = current_app.get_current_user()
    response = None
    if user.is_anonymous or (not user.is_teacher and not user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        data = request.get_json()
        data = data["data"]
        emails = data.get("emails") or []
        whitelist_id = data.get("whitelist_id")

        whitelist = Whitelist.query.filter(Whitelist.id == whitelist_id).first()
        users = User.query.filter(User.email.in_(emails)).all()
        # make sure you don't twice a same user
        whitelist.users.extend([u for u in users if u.id not in [u.id for u in whitelist.users]])

        response = APIResponseFactory.make_response(data={
            "users": [u.serialize() for u in users],
            "whitelist": whitelist.serialize()
        })

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Cannot insert data", "details": str(e)
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/<user_id>/remove-from-whitelist/<whitelist_id>', methods=['DELETE'])
@auth.login_required
def remove_user_from_whitelist(api_version, user_id, whitelist_id):
    """
    :return:
    """
    user = current_app.get_current_user()
    response = None
    if user.is_anonymous or (not user.is_teacher and not user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:

        whitelist = Whitelist.query.filter(Whitelist.id == whitelist_id).first()
        user = User.query.filter(User.id == user_id).first()

        # remove the user from the whitelist
        whitelist.users = [u for u in whitelist.users if u.id != int(user.id)]

        response = APIResponseFactory.make_response(data=[])

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Cannot delete data", "details": str(e)
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/add-whitelist', methods=['POST'])
@auth.login_required
def add_whitelist(api_version):
    """
    {
        data: {
            name : 'My new whitelist'
        }
    }
    :return:
    """
    user = current_app.get_current_user()
    response = None
    if user.is_anonymous or (not user.is_teacher and not user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        data = request.get_json()
        data = data["data"]
        new_whitelist_name = data.get("whitelist_name")

        whitelist = Whitelist(label=new_whitelist_name)
        db.session.add(whitelist)

        try:
            db.session.commit()
            new_id = db.session.query(func.max(Whitelist.id))
            new_whitelist = Whitelist.query.filter(Whitelist.id == new_id).first()
            response = APIResponseFactory.make_response(data={
                "whitelist": new_whitelist.serialize()
            })
        except Exception as e:
            db.session.rollback()
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Cannot insert data", "details": str(e)
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/delete-whitelist/<whitelist_id>', methods=['DELETE'])
@auth.login_required
def delete_whitelist(api_version, whitelist_id):
    """
    :return:
    """
    user = current_app.get_current_user()
    response = None
    if user.is_anonymous or (not user.is_teacher and not user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        try:
            whitelist = Whitelist.query.filter(Whitelist.id == whitelist_id).first()
            # unbind the associated documents
            associated_docs = Document.query.filter(Document.whitelist_id == whitelist.id).all()
            for doc in associated_docs:
                doc.whitelist_id = None
            # then delete the whitelist
            db.session.delete(whitelist)
            db.session.commit()
            response = APIResponseFactory.make_response(data=[])
        except Exception as e:
            db.session.rollback()
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Cannot delete data", "details": str(e)
            })

    return APIResponseFactory.jsonify(response)
