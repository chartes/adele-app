from flask import request, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import Editor
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409


@api_bp.route('/api/<api_version>/editors')
@api_bp.route('/api/<api_version>/editors/<editor_id>')
def api_editor(api_version, editor_id=None):
    if editor_id is None:
        editors = Editor.query.all()
    else:
        # single
        at = Editor.query.filter(Editor.id == editor_id).first()
        if at is None:
            return make_404("Editor {0} not found".format(editor_id))
        else:
            editors = [at]
    return make_200([a.serialize() for a in editors])


@api_bp.route('/api/<api_version>/editors', methods=['DELETE'])
@api_bp.route('/api/<api_version>/editors/<editor_id>', methods=['DELETE'])
@auth.login_required
def api_delete_editor(api_version, editor_id=None):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    if editor_id is None:
        editors = Editor.query.all()
    else:
        editors = Editor.query.filter(Editor.id == editor_id).all()

    for a in editors:
        db.session.delete(a)
    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        return make_409(str(e))


@api_bp.route('/api/<api_version>/editors', methods=['PUT'])
@auth.login_required
def api_put_editor(api_version):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            try:
                modifed_data = []
                for editor in data:
                    a = Editor.query.filter(Editor.id == editor.get('id', None)).one()
                    a.ref = editor.get("ref")
                    a.name = editor.get("name")

                    db.session.add(a)
                    modifed_data.append(a)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return make_409(str(e))

            data = []
            for a in modifed_data:
                r = api_editor(api_version=api_version, editor_id=a.id)
                data.append(json_loads(r.data)["data"])

            return make_200(data)
        else:
            return make_409("no data")
    except NoResultFound:
        return make_404("Editor not found")


@api_bp.route('/api/<api_version>/editors', methods=['POST'])
@auth.login_required
def api_post_editor(api_version):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for editor in data:
                a = Editor(**editor)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_409(str(e))

        data = []
        for a in created_data:
            r = api_editor(api_version=api_version, editor_id=a.id)
            data.append(json_loads(r.data)["data"])

        return make_200(data)
    else:
        return make_409("no data")
