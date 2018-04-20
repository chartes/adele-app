from sqlalchemy.orm.exc import NoResultFound

from app.api.response import APIResponseFactory
from app.api.routes import api_bp
from app.models import User


"""
===========================
    Users
===========================
"""


@api_bp.route('/api/<api_version>/user')
def api_current_user(api_version):
    # TODO: change hard coded id
    try:
        user = User.query.filter(User.id == 1).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "User not found"
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/<user_id>')
def api_users(api_version, user_id):
    try:
        user = User.query.filter(User.id == user_id).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "User {0} not found".format(user_id)
        })
    return APIResponseFactory.jsonify(response)
