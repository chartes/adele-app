from flask import request, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import ActeType
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409


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
@auth.login_required
def api_delete_acte_type(api_version, acte_type_id=None):

    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

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
        return make_409(str(e))


@api_bp.route('/api/<api_version>/acte-types', methods=['PUT'])
@auth.login_required
def api_put_acte_type(api_version):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            try:
                modifed_data = []
                for acte_type in data:
                    a = ActeType.query.filter(ActeType.id == acte_type.get('id')).one()
                    a.label = acte_type.get("label")
                    a.description = acte_type.get("description")

                    db.session.add(a)
                    modifed_data.append(a)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return make_409(str(e))

            data = []
            for a in modifed_data:
                r = api_acte_type(api_version=api_version, acte_type_id=a.id)
                data.append(json_loads(r.data)["data"])

            return make_200(data)
        else:
            return make_409("no data")
    except NoResultFound:
        return make_404("ActeType not found")


@api_bp.route('/api/<api_version>/acte-types', methods=['POST'])
@auth.login_required
def api_post_acte_type(api_version):

    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

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
            return make_409(str(e))

        data = []
        for a in created_data:
            r = api_acte_type(api_version=api_version, acte_type_id=a.id)
            data.append(json_loads(r.data)["data"])

        return make_200(data)
    else:
        return make_409("no data")
