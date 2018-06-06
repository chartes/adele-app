from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import Language


@api_bp.route('/api/<api_version>/languages')
@api_bp.route('/api/<api_version>/languages/<language_code>')
def api_language(api_version, language_code=None):
    try:
        if language_code is not None:
            languages = [Language.query.filter(Language.code== language_code).one()]
        else:
            languages = Language.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in languages])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Language {0} not found".format(language_code)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/languages', methods=['DELETE'])
@api_bp.route('/api/<api_version>/languages/<language_code>', methods=['DELETE'])
@auth.login_required
def api_delete_language(api_version, language_code=None):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if language_code is not None:
                languages = [Language.query.filter(Language.code == language_code).one()]
            else:
                languages = Language.query.all()

            for c in languages:
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
                "status": 404, "title": "Language {0} not found".format(language_code)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/languages', methods=['PUT'])
@auth.login_required
def api_put_language(api_version):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
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
                    for language in data:
                        if "code" not in language:
                            raise Exception("Language code is missing from the payload")
                        a = Language.query.filter(Language.code == language["code"]).one()
                        if "label" in language:
                            a.label = language["label"]
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
                            url_for("api_bp.api_language", api_version=api_version, language_code=a.code)
                        )
                        print(json_obj)
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Language not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/languages', methods=['POST'])
@auth.login_required
def api_post_language(api_version):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
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
                for language in data:
                    if "code" not in language:
                        raise Exception("Language code is missing from the payload")
                    a = Language(**language)
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
                            url_for("api_bp.api_language", api_version=api_version, language_code=a.code)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Language not found"
            })

    return APIResponseFactory.jsonify(response)

