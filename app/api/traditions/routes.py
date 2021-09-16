from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import Tradition
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409, make_400


@api_bp.route('/api/<api_version>/traditions')
@api_bp.route('/api/<api_version>/traditions/<tradition_id>')
def api_tradition(api_version, tradition_id=None):
    if tradition_id is None:
        traditions = Tradition.query.order_by(Tradition.label).all()
    else:
        # single
        at = Tradition.query.filter(Tradition.id == tradition_id).first()
        if at is None:
            return make_404("Tradition {0} not found".format(tradition_id))
        else:
            traditions = [at]
    return make_200([a.serialize() for a in traditions])


@api_bp.route('/api/<api_version>/traditions', methods=['DELETE'])
@api_bp.route('/api/<api_version>/traditions/<tradition_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_tradition(api_version, tradition_id=None):
    if tradition_id is None:
        traditions = Tradition.query.all()
    else:
        traditions = Tradition.query.filter(Tradition.id == tradition_id).all()

    for a in traditions:
        db.session.delete(a)
    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))


@api_bp.route('/api/<api_version>/traditions', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_tradition(api_version):
    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]
            modified_data = []
            try:
                for tradition in data:
                    a = Tradition.query.filter(Tradition.id == tradition.get('id', None)).one()
                    a.label = tradition.get("label")

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
        return make_404("Tradition not found")


@api_bp.route('/api/<api_version>/traditions', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_tradition(api_version):
    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for tradition in data:
                a = Tradition(**tradition)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_409(str(e))

        return make_200([d.serialize() for d in created_data])
    else:
        return make_400("no data")
