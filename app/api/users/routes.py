from flask import request, current_app, jsonify
from flask_jwt_extended import jwt_required
import jwt
from sqlalchemy import func, text
from sqlalchemy.orm.exc import NoResultFound

from app import auth, db
from app.api.response import APIResponseFactory
from app.api.routes import api_bp
from app.models import User, Role, Whitelist, Document
from app.utils import make_200, make_404, forbid_if_nor_teacher_nor_admin, make_409, make_403, make_400, \
    forbid_if_nor_teacher_nor_admin_and_wants_user_data

"""
===========================
    Users
===========================
"""


@api_bp.route('/api/<api_version>/token')
@jwt_required
def get_auth_token(api_version):
    user = current_app.get_current_user()
    token = user.generate_auth_token()
    return make_200(data=[{'token': token.decode('ascii')}])


@api_bp.route('/api/<api_version>/current-user')
def api_current_user(api_version):
    auth_headers = request.headers.get('Authorization', '').split()

    token = auth_headers[1]

    print("token", auth_headers, token)
    data = jwt.decode(token, current_app.config['SECRET_KEY'])
    user = User.query.filter_by(email=data['sub']).first()

    if not user:
        return jsonify({'message': 'Invalid credentials', 'authenticated': False}), 401

    return jsonify({'token': token, 'user_data': user.serialize()})


@api_bp.route('/api/<api_version>/users/<user_id>')
@jwt_required
def api_users(api_version, user_id):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if access_is_forbidden:
        return access_is_forbidden

    target_user = User.query.filter(User.id == user_id).first()

    if target_user is not None:
        return make_200(data=[target_user.serialize()])
    else:
        return make_404()


@api_bp.route('/api/<api_version>/users')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_all_users(api_version):
    page_number = request.args.get('num-page', 1)
    page_size = request.args.get('page-size', 50)

    query = User.query
    total = query.count()

    sort = request.args.get('sort-by', None)
    if sort:
        field, order = sort.split('.')
        query = query.order_by(text("%s %s" % (field, "desc" if order == "asc" else "asc")))

    users = query.paginate(int(page_number), int(page_size), max_per_page=100, error_out=False).items

    return make_200(data={"total": total, "users": [u.serialize() for u in users]})


@api_bp.route('/api/<api_version>/teachers')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_all_teachers(api_version):
    teachers = [u.serialize() for u in User.query.order_by(User.username).all() if u.is_teacher]
    return make_200(data={"users": teachers})


@api_bp.route('/api/<api_version>/users/<user_id>/roles')
@jwt_required
def api_users_roles(api_version, user_id):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if access_is_forbidden:
        return access_is_forbidden

    target_user = User.query.filter(User.id == user_id).first()
    if target_user is not None:
        return make_200(data=[r.serialize() for r in target_user.roles])
    else:
        return make_404()


@api_bp.route('/api/<api_version>/users/<user_id>/roles', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
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
    data = request.get_json()
    if "data" in data:
        data = data["data"]

        user = current_app.get_current_user()
        target_user = User.query.filter(User.id == user_id).first()

        for role_name in [r.get("name", None) for r in data]:

            if not role_name in target_user.roles:
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
            return make_400(str(e))
    else:
        return make_409()


@api_bp.route('/api/<api_version>/users/<user_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_user(api_version, user_id):
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
            return make_400(str(e))

    except NoResultFound:
        return make_404()


@api_bp.route('/api/<api_version>/users/<user_id>/roles', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_users_roles(api_version, user_id):
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
        print(str(e))
        return make_400(str(e))


@api_bp.route('/api/<api_version>/whitelists/<whitelist_id>/add-user/<user_id>', methods=['GET'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def add_user_to_whitelist(api_version, whitelist_id, user_id):

    whitelist = Whitelist.query.filter(Whitelist.id == whitelist_id).first()
    user = User.query.filter(User.id == user_id).first()
    # make sure you don't twice a same user
    if user not in whitelist.users:
        whitelist.users.append(user)

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
@jwt_required
@forbid_if_nor_teacher_nor_admin
def remove_user_from_whitelist(api_version, whitelist_id, user_id):
    """
    :return:
    """
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
@jwt_required
def api_get_whitelist(api_version, whitelist_id):
    w = Whitelist.query.filter(Whitelist.id == whitelist_id).first()
    if w is None:
        return make_404("whitelist unknown")
    else:
        return make_200(data=w.serialize())


@api_bp.route('/api/<api_version>/whitelists')
@jwt_required
def api_get_whitelist_all(api_version):
    whitelists = Whitelist.query.order_by(Whitelist.label).all()
    return make_200(data=[w.serialize() for w in whitelists])

@api_bp.route('/api/<api_version>/whitelists', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_whitelist(api_version):
    """
    {
        data: {
            label : 'My new whitelist'
        }
    }
    :return:
    """
    data = request.get_json()

    try:
        new_whitelist_name = data.get("label")
        whitelist = Whitelist(label=new_whitelist_name)

        whitelist.users = [current_app.get_current_user()]

        db.session.add(whitelist)
        db.session.commit()
        return make_200(data=whitelist.serialize())
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))


@api_bp.route('/api/<api_version>/whitelists/<whitelist_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def delete_whitelist(api_version, whitelist_id):
    """
    :return:
    """
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
        return make_400(str(e))

