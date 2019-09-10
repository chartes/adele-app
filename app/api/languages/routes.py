from flask import request, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import Language
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409


@api_bp.route('/api/<api_version>/languages')
@api_bp.route('/api/<api_version>/languages/<language_code>')
def api_language(api_version, language_code=None):
    if language_code is None:
        languages = Language.query.all()
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
@auth.login_required
def api_delete_language(api_version, language_code=None):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

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
        print(str(e))
        return make_409(str(e))


@api_bp.route('/api/<api_version>/languages', methods=['PUT'])
@auth.login_required
def api_put_language(api_version):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            try:
                modifed_data = []
                for language in data:
                    a = Language.query.filter(Language.code == language.get('code', None)).one()
                    a.label = language.get("label")

                    db.session.add(a)
                    modifed_data.append(a)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return make_409(str(e))

            data = []
            for a in modifed_data:
                r = api_language(api_version=api_version, language_code=a.code)
                data.append(json_loads(r.data)["data"])

            return make_200(data)
        else:
            return make_409("no data")
    except NoResultFound:
        return make_404("Language not found")


@api_bp.route('/api/<api_version>/languages', methods=['POST'])
@auth.login_required
def api_post_language(api_version):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

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

        data = []
        for a in created_data:
            r = api_language(api_version=api_version, language_code=a.code)
            data.append(json_loads(r.data)["data"])

        return make_200(data)
    else:
        return make_409("no data")
