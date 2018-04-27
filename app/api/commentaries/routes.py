from flask import request, url_for
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, get_current_user, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import Commentary


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries')
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>')
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id>')
def api_commentary(api_version, doc_id, user_id=None, type_id=None):
    user = get_current_user()
    response = None

    if user is not None:
        # only teacher and admin can see everything
        if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != int(user.id):
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })

    if response is None:

        if type_id is None:
            type_id = Commentary.type_id
        if user_id is None:
            user_id = Commentary.user_id

        commentaries = Commentary.query.filter(
            Commentary.doc_id == doc_id,
            Commentary.user_id == user_id,
            Commentary.type_id == type_id
        ).all()

        response = APIResponseFactory.make_response(data=[c.serialize() for c in commentaries])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['POST'])
@auth.login_required
def api_post_commentary(api_version, doc_id):
    """
    {
        "data": [
            {
                "doc_id" : 1,
                "user_id" : 1,
                "type_id": 2,
                "content" : "This is a commentary"
            }
        ]
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    response = None
    user = get_current_user()
    if user is None or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        try:
            data = request.get_json()

            if "data" in data:
                data = data["data"]

                if not isinstance(data, list):
                    data = [data]

                created_data = []
                for co in data:

                    if "user_id" not in co:
                        co["user_id"] = user.id

                    # only teacher and admin can see everything
                    if (not user.is_teacher and not user.is_admin) and int(co["user_id"]) != int(user.id):
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Access forbidden"
                        })
                        db.session.rollback()
                        break

                    c = Commentary(doc_id=co["doc_id"], user_id=co["user_id"], type_id=co["type_id"],
                                   content=co["content"])
                    db.session.add(c)
                    created_data.append(c)

                try:
                    db.session.commit()
                except (Exception, KeyError) as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot insert data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for c in created_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_commentary", api_version=api_version,
                                    doc_id=c.doc_id, user_id=c.user_id, type_id=c.type_id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Commentary not found"
            })

    return APIResponseFactory.jsonify(response)