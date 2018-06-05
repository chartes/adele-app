from flask import request, redirect, url_for, current_app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from app import auth, db
from app.api.notes.association_binders import TranscriptionNoteBinder, TranslationNoteBinder, CommentaryNoteBinder
from app.api.response import APIResponseFactory
from app.api.routes import api_bp, query_json_endpoint
from app.api.transcriptions.routes import get_reference_transcription
from app.api.translations.routes import get_reference_translation
from app.models import Transcription, Commentary, Translation, Note, NoteType, Document

"""
===========================
    Notes
===========================
"""


@api_bp.route('/api/<api_version>/notes', methods=['GET', 'POST'])
def api_add_note(api_version):
    note_data = request.get_json()
    # note = Note()
    # dump(data)
    return APIResponseFactory.jsonify({
        'note_data': note_data
    })


@api_bp.route("/api/<api_version>/note-types")
def api_note_types(api_version):
    """

    :param api_version:
    :return:
    """
    try:
        note_types = NoteType.query.all()
        response = APIResponseFactory.make_response(data=[nt.serialize() for nt in note_types])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Types de note introuvables"
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/reference/notes')
def api_documents_transcriptions_reference_notes(api_version, doc_id):
    tr = get_reference_transcription(doc_id)
    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Transcription not found"
        })
    else:
        response = APIResponseFactory.make_response(data=[
            thn.note.serialize() for thn in tr.notes if thn.transcription_id == tr.id
        ])
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/reference/notes')
def api_documents_translations_reference_notes(api_version, doc_id):
    tr = get_reference_translation(doc_id)
    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Translation not found"
        })
    else:
        response = APIResponseFactory.make_response(data=[
            thn.note.serialize() for thn in tr.notes if thn.translation_id == tr.id
        ])
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/reference/notes')
def api_documents_commentaries_reference_notes(api_version, doc_id):
    tr = get_reference_transcription(doc_id)

    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Transcription not found"
        })
    else:
        notes = []
        commentaries = Commentary.query.filter(Commentary.doc_id == doc_id, Commentary.user_id == tr.user_id).all()
        for c in commentaries:
            notes.extend(c.notes)

        response = APIResponseFactory.make_response(data=[n.serialize() for n in notes])
    return APIResponseFactory.jsonify(response)


def api_documents_binder_notes(user, api_version, doc_id, note_id, user_id, binder):
    # sélectionner la liste des notes de <binder> d'un utilisateur pour un doc
    """

    :param note_id:
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    response = None
    if user is None and user_id is not None:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    elif user is None:
        tr = get_reference_translation(doc_id)
        if tr is None:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Translation not found"
            })
        else:
            user_id = tr.user_id
    else:
        if not user.is_teacher and not user.is_admin:
            user_id = user.id

    # only teacher and admin can see everything
    if user is not None:
        if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })

    if response is None:

        all_notes = binder.get_notes(doc_id)

        notes = []
        for note in all_notes:
            if user_id is None:
                if note_id is None:
                    notes.append(note)
                elif int(note_id) == note.id:
                    notes.append(note)
            elif note.user_id == int(user_id):
                if note_id is None:
                    notes.append(note)
                elif int(note_id) == note.id:
                    notes.append(note)

        if response is None:
            if len(notes) == 0:
                response = APIResponseFactory.make_response(errors={
                    "status": 404, "title": "Notes not found"
                })
            else:
                response = APIResponseFactory.make_response(data=[note.serialize() for note in notes])

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes")
@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>")
@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id>")
def api_documents_transcriptions_notes(api_version, doc_id, note_id=None, user_id=None):
    user = current_app.get_current_user()
    return api_documents_binder_notes(user, api_version, doc_id, note_id, user_id, TranscriptionNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes")
@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>")
@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id>")
def api_documents_translations_notes(api_version, doc_id, note_id=None, user_id=None):
    user = current_app.get_current_user()
    return api_documents_binder_notes(user, api_version, doc_id, note_id, user_id, TranslationNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes")
@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>")
@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id>")
def api_documents_commentaries_notes(api_version, doc_id, note_id=None, user_id=None):
    user = current_app.get_current_user()
    return api_documents_binder_notes(user, api_version, doc_id, note_id, user_id, CommentaryNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/notes")
@api_bp.route("/api/<api_version>/documents/<doc_id>/notes/<note_id>")
@api_bp.route("/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id>")
def api_documents_notes(api_version, doc_id, note_id=None, user_id=None):

    user = current_app.get_current_user()
    args = {
        "api_version": api_version,
        "doc_id" : doc_id,
        "user_id" : user_id,
        "note_id": note_id
    }

    data = []
    errors = []

    """
        Transcriptions
    """
    transcriptions_notes = query_json_endpoint(
        request,
        url_for( "api_bp.api_documents_transcriptions_notes", **args), user=user
    )

    if "data" in transcriptions_notes:
        if not isinstance(transcriptions_notes["data"], list):
            transcriptions_notes["data"] = [transcriptions_notes["data"]]
        data.extend(transcriptions_notes["data"])
    else:
        errors.append(transcriptions_notes["errors"])

    """
        Translations
    """
    translations_notes = query_json_endpoint(
        request,
        url_for( "api_bp.api_documents_translations_notes", **args), user=user
    )
    if "data" in translations_notes:
        if not isinstance(translations_notes["data"], list):
            translations_notes["data"] = [translations_notes["data"]]
        data.extend(translations_notes["data"])
    else:
        errors.append(translations_notes["errors"])

    """
        Commentaries
    """
    commentaries_notes = query_json_endpoint(
        request,
        url_for( "api_bp.api_documents_commentaries_notes", **args), user=user
    )
    if "data" in commentaries_notes:
        if not isinstance(commentaries_notes["data"], list):
            commentaries_notes["data"] = [commentaries_notes["data"]]
        data.extend(commentaries_notes["data"])
    else:
        errors.append(commentaries_notes["errors"])

    """
        Make response
    """
    if len(errors) != 0 and len(data) == 0:
        response = APIResponseFactory.make_response(errors=errors)
    else:
        response = APIResponseFactory.make_response(data=data)

    return APIResponseFactory.jsonify(response)


def api_post_documents_binder_notes(request, user, api_version, doc_id, binder):
    """
     {
        "data": [
                {
                    "username": "Eleve1" (optionnal),
                    "transcription_username" : "Eleve1"
                    "note_type": 1,
                    "content": "My first <binder> note",
                    "ptr_start": 1,
                    "ptr_end": 80
                },
                {
                    "username": "Eleve1" (optionnal),
                    "transcription_username" : "AdminJulien"
                    "note_type": 1,
                    "content": "My second <binder> note",
                    "ptr_start": 80,
                    "ptr_end": 96
                }
        ]
    }
    :param api_version:
    :param doc_id:
    :return:
    """

    """
        Use the binder parameter to determine between transcriptions, translations and commentaries
    """

    data = request.get_json()
    response = None
    created_users = set()

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    if "data" in data and response is None:
        data = data["data"]

        if not isinstance(data, list):
            data = [data]

        if response is None:
            # local note id offset
            nb = 0
            # get the <binder> id max
            try:
                note_max_id = db.session.query(func.max(Note.id)).one()
                note_max_id = note_max_id[0] + 1
            except NoResultFound:
                # it is the <binder> for this user and this document
                note_max_id = 1

            for n_data in data:
                # user = current_app.get_current_user()
                user_id = user.id
                # teachers and admins can put/post/delete on others behalf
                if (user.is_teacher or user.is_admin) and "username" in n_data:
                    usr = current_app.get_user_from_username(n_data["username"])
                    if usr is not None:
                        user_id = usr.id

                # on wich <binder> should the note be attached ?
                if (user.is_teacher or user.is_admin) and binder.username_field in n_data:
                    tr_usr = current_app.get_user_from_username(n_data[binder.username_field])
                else:
                    tr_usr = user

                # make the new note
                # TODO gérer erreur
                note_type = NoteType.query.filter(NoteType.id == n_data["note_type"]).first()
                new_note = Note(
                    id=note_max_id + nb + 1,
                    user_id=user_id,
                    content=n_data["content"],
                    type_id=note_type.id,
                    note_type=note_type
                )
                try:
                    new_note = binder.bind(new_note, n_data, tr_usr.id, doc_id)
                except Exception as e:
                    db.session.rollback()
                    new_note = None
                    response = APIResponseFactory.make_response(errors={
                        "status": 404, "title": "Object not found", "details": str(e)
                    })
                    break

                if new_note is not None:
                    db.session.add(new_note)
                    created_users.add((new_note.id, tr_usr))
                    # move local note id offset
                    nb += 1

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot insert data", "details": str(e)
                })

            if response is None:
                created_data = []
                for note_id, tr_usr in created_users:
                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            binder.get_endpoint_name,
                            api_version=api_version,
                            doc_id=doc_id,
                            note_id=note_id
                        ),
                        user=user
                    )
                    created_data.append(json_obj["data"])
                    # TODO gerer "errors"

                response = APIResponseFactory.make_response(data=created_data)

    return APIResponseFactory.jsonify(response)


def api_put_documents_binder_notes(request, user, api_version, doc_id, binder):
    """
     {
        "data": [
                {
                    "note_id" : 1159,
                    "content": "My first <binder> note",
                    "ptr_start": 1,
                    "ptr_end": 80
                },
                {
                    "note_id": 1160,
                    "content": "My second <binder> note",
                    "ptr_start": 80,
                    "ptr_end": 96
                }
        ]
    }
    :param api_version:
    :param doc_id:
    :return:
    """

    """
        Use the binder parameter to determine between transcriptions, translations and commentaries
    """

    data = request.get_json()
    response = None
    updated_notes = set()

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    if "data" in data and response is None:
        data = data["data"]

        if not isinstance(data, list):
            data = [data]

        if response is None:

            for n_data in data:

                try:
                    # todo gérer la secu dans le update
                    updated_note = binder.update(doc_id, n_data)
                    # save which users to retrieve later
                    updated_notes.add(updated_note)
                except NoResultFound:
                    response = APIResponseFactory.make_response(errors={
                        "status": 403,
                        "title": "Update forbidden",
                    })
                    break

                if response is None:
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Cannot update data", "details": str(e)
                        })

            if response is None:
                updated_data = []
                for note in updated_notes:
                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            binder.get_endpoint_name,
                            api_version=api_version,
                            doc_id=doc_id,
                            note_id=note.id
                        ),
                        user=user
                    )
                    updated_data.append(json_obj["data"])

                response = APIResponseFactory.make_response(data=updated_data)

    return APIResponseFactory.jsonify(response)


def api_delete_documents_binder_notes(request, user, api_version, doc_id, user_id, note_id, binder):
    response = None

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    if user is not None:
        if (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })

    # delete transcriptions for the given user id
    if response is None:
        try:
            # bring the transcription to delete

            if note_id is not None:
                note = Note.query.filter(Note.id == note_id).first()
                db.session.delete(note)
            else:
                notes = binder.get_notes(doc_id)
                for note in notes:
                    if note.user_id == int(user_id):
                        db.session.delete(note)
        except NoResultFound:
            pass

        if response is None:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot delete data", "details": str(e)
                })

        if response is None:
            response = APIResponseFactory.make_response(data=[])

    return APIResponseFactory.jsonify(response)


"""
===========================
    POST Notes
===========================
"""


@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes", methods=["POST"])
@auth.login_required
def api_post_documents_transcriptions_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_post_documents_binder_notes(request, user, api_version, doc_id, TranscriptionNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes", methods=["POST"])
@auth.login_required
def api_post_documents_translations_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_post_documents_binder_notes(request, user, api_version, doc_id, TranslationNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes", methods=["POST"])
@auth.login_required
def api_post_documents_commentaries_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_post_documents_binder_notes(request, user, api_version, doc_id, CommentaryNoteBinder)


"""
===========================
    PUT Notes
===========================
"""


@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes", methods=["PUT"])
@auth.login_required
def api_put_documents_transcriptions_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_put_documents_binder_notes(request, user, api_version, doc_id, TranscriptionNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes", methods=["PUT"])
@auth.login_required
def api_put_documents_translations_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_put_documents_binder_notes(request, user, api_version, doc_id, TranslationNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes", methods=["PUT"])
@auth.login_required
def api_put_documents_commentaries_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_put_documents_binder_notes(request, user, api_version, doc_id, CommentaryNoteBinder)


"""
===========================
    DELETE Notes
===========================
"""


@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id>", methods=["DELETE"])
@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>/from-user/<user_id>", methods=["DELETE"])
@auth.login_required
def api_delete_documents_transcriptions_notes(api_version, doc_id, user_id, note_id=None):
    user = current_app.get_current_user()
    return api_delete_documents_binder_notes(request, user, api_version, doc_id, user_id, note_id, TranscriptionNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id>", methods=["DELETE"])
@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>/from-user/<user_id>", methods=["DELETE"])
@auth.login_required
def api_delete_documents_translations_notes(api_version, doc_id, user_id, note_id=None):
    user = current_app.get_current_user()
    return api_delete_documents_binder_notes(request, user, api_version, doc_id, user_id, note_id, TranslationNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id>", methods=["DELETE"])
@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>/from-user/<user_id>", methods=["DELETE"])
@auth.login_required
def api_delete_documents_commentaries_notes(api_version, doc_id, user_id, note_id=None):
    user = current_app.get_current_user()
    return api_delete_documents_binder_notes(request, user, api_version, doc_id, user_id, note_id, CommentaryNoteBinder)

