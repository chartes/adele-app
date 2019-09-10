from flask import request, current_app
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
@auth.login_required
def api_delete_commentary_type(api_version, commentary_type_id=None):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

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
@auth.login_required
def api_put_commentary_type(api_version):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            try:
                modifed_data = []
                for commentary_type in data:
                    a = CommentaryType.query.filter(CommentaryType.id == commentary_type.get('id', None)).one()
                    a.label = commentary_type.get("label")

                    db.session.add(a)
                    modifed_data.append(a)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return make_409(str(e))

            data = []
            for a in modifed_data:
                r = api_commentary_type(api_version=api_version, commentary_type_id=a.id)
                data.append(json_loads(r.data)["data"])

            return make_200(data)
        else:
            return make_409("no data")
    except NoResultFound:
        return make_404("CommentaryType not found")


@api_bp.route('/api/<api_version>/commentary-types', methods=['POST'])
@auth.login_required
def api_post_commentary_type(api_version):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

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

        data = []
        for a in created_data:
            r = api_commentary_type(api_version=api_version, commentary_type_id=a.id)
            data.append(json_loads(r.data)["data"])

        return make_200(data)
    else:
        return make_409("no data")
