from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import Editor


@api_bp.route('/api/<api_version>/editors')
@api_bp.route('/api/<api_version>/editors/<editor_id>')
def api_editor(api_version, editor_id=None):
    try:
        if editor_id is not None:
            editors = [Editor.query.filter(Editor.id == editor_id).one()]
        else:
            editors = Editor.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in editors])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Editor {0} not found".format(editor_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/editors', methods=['DELETE'])
@api_bp.route('/api/<api_version>/editors/<editor_id>', methods=['DELETE'])
@auth.login_required
def api_delete_editor(api_version, editor_id=None):
    response = None
    user = current_app.get_current_user()
    if user is None or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if editor_id is not None:
                editors = [Editor.query.filter(Editor.id == editor_id).one()]
            else:
                editors = Editor.query.all()

            for c in editors:
                db.session.delete(c)
            try:
                db.session.commit()
                response = APIResponseFactory.make_response(data=[])
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot delete data", "details": str(e)
                })

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Editor {0} not found".format(editor_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/editors', methods=['PUT'])
@auth.login_required
def api_put_editor(api_version):
    response = None
    user = current_app.get_current_user()
    if user is None or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            data = request.get_json()

            if "data" in data:
                data = data["data"]

                if not isinstance(data, list):
                    data = [data]

                modifed_data = []
                try:
                    for editor in data:
                        if "id" not in editor:
                            raise Exception("Editor id is missing from the payload")
                        a = Editor.query.filter(Editor.id == editor["id"]).one()
                        if "ref" in editor:
                            a.ref = editor["ref"]
                        if "name" in editor:
                            a.name = editor["name"]
                        db.session.add(a)
                        modifed_data.append(a)

                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot update data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for a in modifed_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_editor", api_version=api_version, editor_id=a.id)
                        )
                        print(json_obj)
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Editor not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/editors', methods=['POST'])
@auth.login_required
def api_post_editor(api_version):
    response = None
    user = current_app.get_current_user()
    if user is None or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            data = request.get_json()

            if "data" in data:
                data = data["data"]

                if not isinstance(data, list):
                    data = [data]

                created_data = []
                for editor in data:
                    if "id" in editor:
                        editor.pop("id")
                    a = Editor(**editor)
                    db.session.add(a)
                    created_data.append(a)

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot insert data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for a in created_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_editor", api_version=api_version, editor_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Editor not found"
            })

    return APIResponseFactory.jsonify(response)

