import pprint
from flask import request, url_for, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from app import auth, db
from app.api.notes.association_binders import TranscriptionNoteBinder, TranslationNoteBinder, CommentaryNoteBinder
from app.api.response import APIResponseFactory
from app.api.routes import api_bp, query_json_endpoint
from app.models import Commentary, Note, NoteType, Document, User, Translation, TranslationHasNote, Transcription, \
    TranscriptionHasNote

"""
===========================
    Notes
===========================
"""


@api_bp.route('/api/<api_version>/notes', methods=['POST', 'PUT'])
@jwt_required
def api_add_note(api_version):
    """
    {
        "data": [
                {
                    "username": "Eleve1",
                    "content": "My first note",
                    "type_id": 0
                },
                {
                    "username": "Eleve2",
                    "content": "My second note",
                    "type_id": 0
                }
        ]
    }
    :param api_version:
    :return:
    """
    user = current_app.get_current_user()
    response = None
    data = request.get_json()

    if "data" in data and response is None:
        data = data["data"]
        if not isinstance(data, list):
            data = [data]
        # find the correct user_id
        for note_data in data:
            note_data["user_id"] = user.id
            if "username" in note_data:
                if (not user.is_teacher and not user.is_admin) and note_data["username"] != user.username:
                    response = APIResponseFactory.make_response(errors={
                        "status": 403,
                        "title": "Insert forbidden",
                    })
                    break
                if note_data["username"] != user.username:
                    u = User.query.filter(User.username == note_data["username"]).one()
                    note_data["user_id"] = u.id
            else:
                note_data["username"] = user.username

        # insert/update the notes
        notes = []
        if response is None:
            try:
                if request.method == 'POST':
                    for note_data in data:
                        new_note = Note(
                            type_id=note_data["type_id"],
                            user_id=note_data["user_id"],
                            content=note_data["content"]
                        )
                        notes.append(new_note)
                else:
                    # method is PUT
                    for note_data in data:
                        note = Note.query.filter(Note.id == note_data["id"]).one()
                        if note is None:
                            raise NoResultFound("Note %s not found" % note_data["id"])
                        note.type_id = note_data["type_id"]
                        note.user_id = note_data["user_id"]
                        note.content = note_data["content"]
                        notes.append(note)

            except (NoResultFound, KeyError) as e:
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot insert or update data", "details": "%s %s" % (type(e), str(e))
                })

        if response is None:
            try:
                db.session.add_all(notes)
                db.session.commit()
                response = APIResponseFactory.make_response(data=[note.serialize() for note in notes])
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot insert data", "details": str(e)
                })

    return APIResponseFactory.jsonify(response)


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
    from app.api.transcriptions.routes import get_reference_transcription
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
    from app.api.translations.routes import get_reference_translation
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
    from app.api.transcriptions.routes import get_reference_transcription
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
    if user.is_anonymous and user_id is not None:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    elif user.is_anonymous:
        from app.api.transcriptions.routes import get_reference_transcription
        tr = get_reference_transcription(doc_id)
        if tr is None:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Transcription not found"
            })
        else:
            user_id = tr.user_id
    else:
        if not user.is_teacher and not user.is_admin:
            user_id = user.id

    # only teacher and admin can see everything
    if not user.is_anonymous:
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

    if user.is_anonymous:
        response = APIResponseFactory.make_response(data=[])
        return APIResponseFactory.jsonify(response)

    if not (user.is_admin or user.is_teacher):
        user_id = user.id
    print(user.id, user_id)
    notes = Note.query.filter(Note.user_id == user_id).all()
    response = APIResponseFactory.make_response(data=[n.serialize() for n in notes])
    return APIResponseFactory.jsonify(response)

    args = {
        "api_version": api_version,
        "doc_id": doc_id,
        "user_id": user_id,
        "note_id": note_id
    }

    data = []
    errors = []

    """
        Transcriptions
    """
    transcriptions_notes = query_json_endpoint(
        request,
        url_for("api_bp.api_documents_transcriptions_notes", **args), user=user
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
        url_for("api_bp.api_documents_translations_notes", **args), user=user
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
        url_for("api_bp.api_documents_commentaries_notes", **args), user=user
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
        # remove duplicates (eg. a note from commentary is the same as the note from the transcription)
        dedup_data = {}
        for d in data:
            dedup_data[d["id"]] = d
        data = list(dedup_data.values())

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
                    id=note_max_id + nb,
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
                    if updated_note:
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

    if not user.is_anonymous:
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
@jwt_required
def api_post_documents_transcriptions_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_post_documents_binder_notes(request, user, api_version, doc_id, TranscriptionNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes", methods=["POST"])
@jwt_required
def api_post_documents_translations_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_post_documents_binder_notes(request, user, api_version, doc_id, TranslationNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes", methods=["POST"])
@jwt_required
def api_post_documents_commentaries_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_post_documents_binder_notes(request, user, api_version, doc_id, CommentaryNoteBinder)


"""
===========================
    PUT Notes
===========================
"""


@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes", methods=["PUT"])
@jwt_required
def api_put_documents_transcriptions_notes(api_version, doc_id):
    user = current_app.get_current_user()

    #delete the notes binding not present in the payload
    if user.is_admin or user.is_teacher:
        data = request.get_json()
        if not isinstance(data["data"], list):
            data = [data["data"]]
        for txt in data:
            if "transcription_username" in data:
                usr = User.query.filter(User.username == txt["transcription_username"]).first()
                user_id = usr.id
            else:
                user_id = user.id
            t = Transcription.query.filter(Transcription.doc_id == doc_id, Transcription.user_id == user_id).first()
            if t:
                for thn in TranscriptionHasNote.query.filter(TranscriptionHasNote.transcription_id == t.id).all():
                    db.session.delete(thn)
                db.session.commit()

    return api_put_documents_binder_notes(request, user, api_version, doc_id, TranscriptionNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes", methods=["PUT"])
@jwt_required
def api_put_documents_translations_notes(api_version, doc_id):
    user = current_app.get_current_user()

    #delete the notes binding not present in the payload
    if user.is_admin or user.is_teacher:
        data = request.get_json()
        if not isinstance(data["data"], list):
            data = [data["data"]]
        for txt in data:
            if "translation_username" in data:
                usr = User.query.filter(User.username == txt["translation_username"]).first()
                user_id = usr.id
            else:
                user_id = user.id
            t = Translation.query.filter(Translation.doc_id == doc_id, Translation.user_id == user_id).first()
            if t:
                for thn in TranslationHasNote.query.filter(TranslationHasNote.translation_id == t.id).all():
                    db.session.delete(thn)
                db.session.commit()

    return api_put_documents_binder_notes(request, user, api_version, doc_id, TranslationNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes", methods=["PUT"])
@jwt_required
def api_put_documents_commentaries_notes(api_version, doc_id):
    user = current_app.get_current_user()
    return api_put_documents_binder_notes(request, user, api_version, doc_id, CommentaryNoteBinder)


"""
===========================
    DELETE Notes
===========================
"""


@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id>", methods=["DELETE"])
@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>/from-user/<user_id>",
              methods=["DELETE"])
@jwt_required
def api_delete_documents_transcriptions_notes(api_version, doc_id, user_id, note_id=None):
    user = current_app.get_current_user()
    return api_delete_documents_binder_notes(request, user, api_version, doc_id, user_id, note_id,
                                             TranscriptionNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id>", methods=["DELETE"])
@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>/from-user/<user_id>",
              methods=["DELETE"])
@jwt_required
def api_delete_documents_translations_notes(api_version, doc_id, user_id, note_id=None):
    user = current_app.get_current_user()
    return api_delete_documents_binder_notes(request, user, api_version, doc_id, user_id, note_id,
                                             TranslationNoteBinder)


@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id>", methods=["DELETE"])
@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>/from-user/<user_id>",
              methods=["DELETE"])
@jwt_required
def api_delete_documents_commentaries_notes(api_version, doc_id, user_id, note_id=None):
    user = current_app.get_current_user()
    return api_delete_documents_binder_notes(request, user, api_version, doc_id, user_id, note_id, CommentaryNoteBinder)
