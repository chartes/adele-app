from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint, json_loads
from app.models import ActeType
from app.utils import forbid_if_nor_teacher_nor_admin


@api_bp.route('/api/<api_version>/acte-types')
@api_bp.route('/api/<api_version>/acte-types/<acte_type_id>')
def api_acte_type(api_version, acte_type_id=None):
    if acte_type_id is None:
        acte_types = ActeType.query.all()
    else:
        # single
        at = ActeType.query.filter(ActeType.id == acte_type_id).first()
        if at is None:
            return APIResponseFactory.make_response(status=404, errors={
                "status": 404, "title": "ActeType {0} not found".format(acte_type_id)
            })
        else:
            acte_types = [at]
    return APIResponseFactory.make_response(status=200, data=[a.serialize() for a in acte_types])


@api_bp.route('/api/<api_version>/acte-types', methods=['DELETE'])
@api_bp.route('/api/<api_version>/acte-types/<acte_type_id>', methods=['DELETE'])
@auth.login_required
def api_delete_acte_type(api_version, acte_type_id=None):

    user_role_is_correct, access_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if not user_role_is_correct:
        return access_forbidden

    try:
        if acte_type_id is None:
            acte_types = ActeType.query.all()
        else:
            acte_types = [ActeType.query.filter(ActeType.id == acte_type_id).one()]

        for a in acte_types:
            db.session.delete(a)
        try:
            db.session.commit()
            return APIResponseFactory.make_response(status=200, data=[])
        except Exception as e:
            db.session.rollback()
            return APIResponseFactory.make_response(status=409, errors={
                "status": 409, "title": "Cannot delete data", "details": str(e)
            })

    except NoResultFound:
        return APIResponseFactory.make_response(status=404, errors={
            "status": 404, "title": "ActeType {0} not found".format(acte_type_id)
        })

@api_bp.route('/api/<api_version>/acte-types', methods=['PUT'])
@auth.login_required
def api_put_acte_type(api_version):

    user_role_is_correct, access_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if not user_role_is_correct:
        return access_forbidden

    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            if not isinstance(data, list):
                data = [data]
            try:
                modifed_data = []
                for acte_type in data:
                    a = ActeType.query.filter(ActeType.id == acte_type["id"]).one()
                    a.label = acte_type.get("label")
                    a.description = acte_type.get("description")

                    db.session.add(a)
                    modifed_data.append(a)
                db.session.commit()
            except NoResultFound as e:
                db.session.rollback()
                return APIResponseFactory.make_response(status=404, errors={
                    "status": 404, "title": "Cannot update data", "details": str(e)
                })
            except Exception as e:
                db.session.rollback()
                return APIResponseFactory.make_response(status=409, errors={
                    "status": 409, "title": "Cannot update data", "details": str(e)
                })

            data = []
            for a in modifed_data:
                r = api_acte_type(api_version=api_version, acte_type_id=a.id)
                data.append(json_loads(r.data)["data"])

            return APIResponseFactory.make_response(status=200, data=data)

    except NoResultFound:
        return APIResponseFactory.make_response(status=404, errors={
            "status": 404, "title": "ActeType not found"
        })


@api_bp.route('/api/<api_version>/acte-types', methods=['POST'])
@auth.login_required
def api_post_acte_type(api_version):
    user_role_is_correct, access_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if not user_role_is_correct:
        return access_forbidden

    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            if not isinstance(data, list):
                data = [data]

            created_data = []
            try:
                for acte_type in data:
                    a = ActeType(**acte_type)
                    db.session.add(a)
                    created_data.append(a)

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return APIResponseFactory.make_response(status=409, errors={
                    "status": 409, "title": "Cannot insert data", "details": str(e)
                })

            data = []
            for a in created_data:
                r = api_acte_type(api_version=api_version, acte_type_id=a.id)
                data.append(json_loads(r.data)["data"])

            return APIResponseFactory.make_response(status=200, data=data)

    except NoResultFound:
        return APIResponseFactory.make_response(status=404, errors={
            "status": 404, "title": "ActeType not found"
        })

