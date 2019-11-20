from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import SpeechPartType
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409, make_400


@api_bp.route('/api/<api_version>/speech-part-types')
@api_bp.route('/api/<api_version>/speech-part-types/<speech_part_type_id>')
def api_speech_part_type(api_version, speech_part_type_id=None):
    if speech_part_type_id is None:
        speech_part_types = SpeechPartType.query.all()
    else:
        # single
        at = SpeechPartType.query.filter(SpeechPartType.id == speech_part_type_id).first()
        if at is None:
            return make_404("SpeechPartType {0} not found".format(speech_part_type_id))
        else:
            speech_part_types = [at]
    return make_200([a.serialize() for a in speech_part_types])


@api_bp.route('/api/<api_version>/speech-part-types', methods=['DELETE'])
@api_bp.route('/api/<api_version>/speech-part-types/<speech_part_type_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_speech_part_type(api_version, speech_part_type_id=None):
    if speech_part_type_id is None:
        speech_part_types = SpeechPartType.query.all()
    else:
        speech_part_types = SpeechPartType.query.filter(SpeechPartType.id == speech_part_type_id).all()

    for a in speech_part_types:
        db.session.delete(a)
    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))


@api_bp.route('/api/<api_version>/speech-part-types', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_speech_part_type(api_version):
    try:
        data = request.get_json()
        if "data" in data:
            data = data["data"]

            try:
                modified_data = []
                for speech_part_type in data:
                    a = SpeechPartType.query.filter(SpeechPartType.id == speech_part_type.get('id')).one()
                    a.label = speech_part_type.get("label")
                    a.lang_code = speech_part_type.get("lang_code")
                    a.description = speech_part_type.get("description")
                    db.session.add(a)
                    modified_data.append(a)
                db.session.commit()
            except Exception as e:
                print(str(e), speech_part_type)
                db.session.rollback()
                return make_409(str(e))

            return make_200([d.serialize() for d in modified_data])
        else:
            return make_400("no data")
    except NoResultFound:
        return make_404("SpeechPartType not found")


@api_bp.route('/api/<api_version>/speech-part-types', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_speech_part_type(api_version):
    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for speech_part_type in data:
                a = SpeechPartType(**speech_part_type)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            print(str(e))
            db.session.rollback()
            return make_400(str(e))

        return make_200([d.serialize() for d in created_data])
    else:
        return make_400("no data")
