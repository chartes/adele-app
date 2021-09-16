from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import Institution
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409, make_400


@api_bp.route('/api/<api_version>/institutions')
@api_bp.route('/api/<api_version>/institutions/<institution_id>')
def api_institution(api_version, institution_id=None):
    if institution_id is None:
        institutions = Institution.query.order_by(Institution.name).all()
    else:
        # single
        at = Institution.query.filter(Institution.id == institution_id).first()
        if at is None:
            return make_404("Institution {0} not found".format(institution_id))
        else:
            institutions = [at]
    return make_200([a.serialize() for a in institutions])


@api_bp.route('/api/<api_version>/institutions', methods=['DELETE'])
@api_bp.route('/api/<api_version>/institutions/<institution_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_institution(api_version, institution_id=None):
    if institution_id is None:
        institutions = Institution.query.all()
    else:
        institutions = Institution.query.filter(Institution.id == institution_id).all()

    for a in institutions:
        db.session.delete(a)
    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))


@api_bp.route('/api/<api_version>/institutions', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_institution(api_version):
    try:
        data = request.get_json()
        if "data" in data:
            data = data["data"]
            modified_data = []
            try:
                for institution in data:
                    a = Institution.query.filter(Institution.id == institution.get('id')).one()
                    a.ref = institution.get("ref")
                    a.name = institution.get("name")

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
        return make_404("Institution not found")


@api_bp.route('/api/<api_version>/institutions', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_institution(api_version):
    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for institution in data:
                a = Institution(**institution)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_400(str(e))

        return make_200([d.serialize() for d in created_data])
    else:
        return make_400("no data")
