from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import ActeType
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409, make_400


@api_bp.route('/api/<api_version>/acte-types')
@api_bp.route('/api/<api_version>/acte-types/<acte_type_id>')
def api_acte_type(api_version, acte_type_id=None):
    if acte_type_id is None:
        acte_types = ActeType.query.all()
    else:
        # single
        at = ActeType.query.filter(ActeType.id == acte_type_id).first()
        if at is None:
            return make_404("ActeType {0} not found".format(acte_type_id))
        else:
            acte_types = [at]
    return make_200([a.serialize() for a in acte_types])


@api_bp.route('/api/<api_version>/acte-types', methods=['DELETE'])
@api_bp.route('/api/<api_version>/acte-types/<acte_type_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_acte_type(api_version, acte_type_id=None):

    if acte_type_id is None:
        acte_types = ActeType.query.all()
    else:
        acte_types = ActeType.query.filter(ActeType.id == acte_type_id).all()

    for a in acte_types:
        db.session.delete(a)
    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))


@api_bp.route('/api/<api_version>/acte-types', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_acte_type(api_version):
    try:
        data = request.get_json()
        if "data" in data:
            data = data["data"]

            try:
                modified_data = []
                for acte_type in data:
                    a = ActeType.query.filter(ActeType.id == acte_type.get('id')).one()
                    a.label = acte_type.get("label")
                    a.description = acte_type.get("description")

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
        return make_404("ActeType not found")


@api_bp.route('/api/<api_version>/acte-types', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_acte_type(api_version):
    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for acte_type in data:
                a = ActeType(**acte_type)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_400(str(e))

        return make_200([d.serialize() for d in created_data])
    else:
        return make_400("no data")
