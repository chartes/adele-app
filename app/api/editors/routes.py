from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import Editor
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409, make_400


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
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_editor(api_version, editor_id=None):
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
        return make_400(str(e))


@api_bp.route('/api/<api_version>/editors', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_editor(api_version):
    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]
            modified_data = []
            try:
                for editor in data:
                    a = Editor.query.filter(Editor.id == editor.get('id', None)).one()
                    a.ref = editor.get("ref")
                    a.name = editor.get("name")

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
        return make_404("Editor not found")


@api_bp.route('/api/<api_version>/editors', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_editor(api_version):
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

        return make_200([d.serialize() for d in created_data])
    else:
        return make_400("no data")
