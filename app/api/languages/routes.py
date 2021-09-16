from flask import request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import Language
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409, make_400


@api_bp.route('/api/<api_version>/languages')
@api_bp.route('/api/<api_version>/languages/<language_code>')
def api_language(api_version, language_code=None):
    if language_code is None:
        languages = Language.query.order_by(Language.label).all()
    else:
        # single
        at = Language.query.filter(Language.code == language_code).first()
        if at is None:
            return make_404("Language {0} not found".format(language_code))
        else:
            languages = [at]
    return make_200([a.serialize() for a in languages])


@api_bp.route('/api/<api_version>/languages', methods=['DELETE'])
@api_bp.route('/api/<api_version>/languages/<language_code>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_language(api_version, language_code=None):
    if language_code is None:
        languages = Language.query.all()
    else:
        languages = Language.query.filter(Language.code == language_code).all()

    for a in languages:
        db.session.delete(a)
    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))


@api_bp.route('/api/<api_version>/languages', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_language(api_version):
    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]
            modified_data = []

            try:
                for language in data:
                    a = Language.query.filter(Language.code == language.get('code', None)).one()
                    a.label = language.get("label")

                    db.session.add(a)
                    modified_data.append(a)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return make_409(str(e))

            return make_200([d.serialize() for d in modified_data])
        else:
            return make_400("no data")
    except NoResultFound:
        return make_404("Language not found")


@api_bp.route('/api/<api_version>/languages', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_language(api_version):
    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for language in data:
                a = Language(**language)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_409(str(e))

        return make_200([d.serialize() for d in created_data])
    else:
        return make_400("no data")
