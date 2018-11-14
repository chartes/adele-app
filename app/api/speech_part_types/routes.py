from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import SpeechPartType


@api_bp.route('/api/<api_version>/speech-part-types')
@api_bp.route('/api/<api_version>/speech-part-types/<speech_part_type_id>')
def api_speech_part_type(api_version, speech_part_type_id=None):
    try:
        if speech_part_type_id is not None:
            countries = [SpeechPartType.query.filter(SpeechPartType.id == speech_part_type_id).one()]
        else:
            countries = SpeechPartType.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in countries])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "SpeechPartType {0} not found".format(speech_part_type_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/speech-part-types', methods=['DELETE'])
@api_bp.route('/api/<api_version>/speech-part-types/<speech_part_type_id>', methods=['DELETE'])
@auth.login_required
def api_delete_speech_part_type(api_version, speech_part_type_id=None):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if speech_part_type_id is not None:
                countries = [SpeechPartType.query.filter(SpeechPartType.id == speech_part_type_id).one()]
            else:
                countries = SpeechPartType.query.all()

            for c in countries:
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
                "status": 404, "title": "SpeechPartType {0} not found".format(speech_part_type_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/speech-part-types', methods=['PUT'])
@auth.login_required
def api_put_speech_part_type(api_version):
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
                    for speech_part_type in data:
                        if "id" not in speech_part_type:
                            raise Exception("SpeechPartType id is missing from the payload")
                        a = SpeechPartType.query.filter(SpeechPartType.id == speech_part_type["id"]).one()
                        if "lang_code" in speech_part_type:
                            a.lang_code = speech_part_type["lang_code"]
                        if "label" in speech_part_type:
                            a.label = speech_part_type["label"]
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
                            url_for("api_bp.api_speech_part_type", api_version=api_version, speech_part_type_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "SpeechPartType not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/speech-part-types', methods=['POST'])
@auth.login_required
def api_post_speech_part_type(api_version):
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
                for speech_part_type in data:
                    if "id" in speech_part_type:
                        speech_part_type.pop("id")
                    a = SpeechPartType(**speech_part_type)
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
                            url_for("api_bp.api_speech_part_type", api_version=api_version, speech_part_type_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "SpeechPartType not found"
            })

    return APIResponseFactory.jsonify(response)

