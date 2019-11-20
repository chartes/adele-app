from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import CommentaryType
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409


@api_bp.route('/api/<api_version>/commentary-types')
@api_bp.route('/api/<api_version>/commentary-types/<commentary_type_id>')
def api_commentary_type(api_version, commentary_type_id=None):
    if commentary_type_id is None:
        commentary_types = CommentaryType.query.all()
    else:
        # single
        at = CommentaryType.query.filter(CommentaryType.id == commentary_type_id).first()
        if at is None:
            return make_404("CommentaryType {0} not found".format(commentary_type_id))
        else:
            commentary_types = [at]
    return make_200([a.serialize() for a in commentary_types])


@api_bp.route('/api/<api_version>/commentary-types', methods=['DELETE'])
@api_bp.route('/api/<api_version>/commentary-types/<commentary_type_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_commentary_type(api_version, commentary_type_id=None):
    if commentary_type_id is None:
        commentary_types = CommentaryType.query.all()
    else:
        commentary_types = CommentaryType.query.filter(CommentaryType.id == commentary_type_id).all()

    for a in commentary_types:
        db.session.delete(a)
    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        return make_409(str(e))


@api_bp.route('/api/<api_version>/commentary-types', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_commentary_type(api_version):
    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            try:
                modified_data = []
                for commentary_type in data:
                    a = CommentaryType.query.filter(CommentaryType.id == commentary_type.get('id', None)).one()
                    a.label = commentary_type.get("label")

                    db.session.add(a)
                    modified_data.append(a)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return make_409(str(e))

            return make_200([d.serialize() for d in modified_data])
        else:
            return make_409("no data")
    except NoResultFound:
        return make_404("CommentaryType not found")


@api_bp.route('/api/<api_version>/commentary-types', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_commentary_type(api_version):
    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for commentary_type in data:
                a = CommentaryType(**commentary_type)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_409(str(e))

        return make_200([d.serialize() for d in created_data])
    else:
        return make_409("no data")
