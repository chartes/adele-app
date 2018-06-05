from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import CommentaryType


@api_bp.route('/api/<api_version>/commentary-types')
@api_bp.route('/api/<api_version>/commentary-types/<commentary_type_id>')
def api_commentary_type(api_version, commentary_type_id=None):
    try:
        if commentary_type_id is not None:
            commentary_types = [CommentaryType.query.filter(CommentaryType.id == commentary_type_id).one()]
        else:
            commentary_types = CommentaryType.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in commentary_types])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "CommentaryType {0} not found".format(commentary_type_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/commentary-types', methods=['DELETE'])
@api_bp.route('/api/<api_version>/commentary-types/<commentary_type_id>', methods=['DELETE'])
@auth.login_required
def api_delete_commentary_type(api_version, commentary_type_id=None):
    response = None
    user = current_app.get_current_user()
    if user is None or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if commentary_type_id is not None:
                commentary_types = [CommentaryType.query.filter(CommentaryType.id == commentary_type_id).one()]
            else:
                commentary_types = CommentaryType.query.all()

            for c in commentary_types:
                db.session.delete(c)
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
                "status": 404, "title": "CommentaryType {0} not found".format(commentary_type_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/commentary-types', methods=['PUT'])
@auth.login_required
def api_put_commentary_type(api_version):
    response = None
    user = current_app.get_current_user()
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

                modifed_data = []
                try:
                    for commentary_type in data:
                        if "id" not in commentary_type:
                            raise Exception("CommentaryType id is missing from the payload")
                        a = CommentaryType.query.filter(CommentaryType.id == commentary_type["id"]).one()
                        if "label" in commentary_type:
                            a.label = commentary_type["label"]
                        db.session.add(a)
                        modifed_data.append(a)

                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot update data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for a in modifed_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_commentary_type", api_version=api_version, commentary_type_id=a.id)
                        )
                        print(json_obj)
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "CommentaryType not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/commentary-types', methods=['POST'])
@auth.login_required
def api_post_commentary_type(api_version):
    response = None
    user = current_app.get_current_user()
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
                for commentary_type in data:
                    if "id" in commentary_type:
                        commentary_type.pop("id")
                    a = CommentaryType(**commentary_type)
                    db.session.add(a)
                    created_data.append(a)

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot insert data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for a in created_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_commentary_type", api_version=api_version, commentary_type_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "CommentaryType not found"
            })

    return APIResponseFactory.jsonify(response)

