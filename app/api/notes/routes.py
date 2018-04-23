from flask import request, redirect, url_for
from sqlalchemy.orm.exc import NoResultFound

from app import get_current_user, auth, get_user_from_username, db
from app.api.response import APIResponseFactory
from app.api.routes import api_bp, query_json_endpoint
from app.api.transcriptions.routes import get_reference_transcription
from app.api.translations.routes import get_reference_translation
from app.models import Transcription, Commentary, Translation, Note, NoteType, Document, TranslationHasNote, \
    TranscriptionHasNote


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


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/reference/notes')
def api_documents_transcriptions_reference_notes(api_version, doc_id):
    tr = get_reference_transcription(doc_id)
    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Transcription not found"
        })
    else:
        #TODO filtrer le user_id
        response = APIResponseFactory.make_response(data=[thn.note.serialize() for thn in tr.notes])
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/reference/notes')
def api_documents_translations_reference_notes(api_version, doc_id):
    tr = get_reference_translation(doc_id)
    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Translation not found"
        })
    else:
        response = APIResponseFactory.make_response(data=[thn.note.serialize() for thn in tr.notes])
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


@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes")
@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id>")
def api_documents_transcriptions_notes(api_version, doc_id, user_id=None):
    # sélectionner la liste des notes de transcription d'un utilisateur pour un doc
    """

    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """

    user = get_current_user()
    if user is None:
        return redirect(url_for("api_bp.api_documents_transcriptions_reference_notes", api_version="1.0", doc_id=doc_id))

    response = None
    # only teacher and admin can see everything
    if (not user.is_teacher and not user.is_admin) and user_id is not None and user_id != user.id:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        if user_id is None:
            user_id = user.id
        else:
            user_id = int(user_id)

        notes = []
        try:
            transcriptions = Transcription.query.filter(Transcription.doc_id == doc_id, Transcription.user_id == user.id).all()
            for tr in transcriptions:
                notes.extend([thn for thn in tr.notes if thn.note.user_id == user_id])
        except NoResultFound:
            pass

        if response is None:
            response = APIResponseFactory.make_response(data=[thn.note.serialize() for thn in notes])

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes")
@api_bp.route("/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id>")
def api_documents_translations_notes(api_version, doc_id, user_id=None):
    # sélectionner la liste des notes de traduction d'un utilisateur pour un doc
    """

    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    user = get_current_user()
    if user is None:
        return redirect(url_for("api_bp.api_documents_translations_reference_notes", api_version="1.0", doc_id=doc_id))

    response = None
    # only teacher and admin can see everything
    if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != int(user.id):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        if user_id is None:
            user_id = user.id
        else:
            user_id = int(user_id)

        notes = []
        try:
            translations = Translation.query.filter(Translation.doc_id == doc_id,
                                                      Translation.user_id == user.id).all()
            for tr in translations:
                notes.extend([thn for thn in tr.notes if thn.note.user_id == user_id])
        except NoResultFound:
            pass

        if response is None:
            response = APIResponseFactory.make_response(data=[thn.note.serialize() for thn in notes])

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes")
@api_bp.route("/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id>")
def api_documents_commentaries_notes(api_version, doc_id, user_id=None):
    # sélectionner la liste des notes de commentaire d'un utilisateur pour un doc
    """

    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """

    user = get_current_user()
    response = None
    if user is None:
        # get the reference transcription
        tr = get_reference_transcription(doc_id)
        user_id = tr.user_id

    else:
        # only teacher and admin can see everything
        if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != int(user.id):
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
    if response is None:
        if user_id is None:
            user_id = user.id
        else:
            user_id = int(user_id)

        notes = []
        try:
            commentaries = Commentary.query.filter(Commentary.doc_id == doc_id,
                                                   Commentary.user_id == user.id).all()
            for c in commentaries:
                notes.extend([n for n in c.notes if n.user_id == user_id])
        except NoResultFound:
            pass

        if response is None:
            response = APIResponseFactory.make_response(data=[note.serialize() for note in notes])

    return APIResponseFactory.jsonify(response)


def make_note_from_data(user_id, data, src=None):
    """
    :param src:
    :param user_id:
    :param data:
    :param kind_of_note: transcription | translation | commentary
    :return:
    """
    note = None

    if isinstance(src, Transcription):
        # TODO: todo gérer erreur
        note_type = NoteType.query.filter(NoteType.id == data["note_type"]).first()
        note = Note(user_id=user_id, content=data["content"], type_id=note_type.id, note_type=note_type)
        transcription_has_note = TranscriptionHasNote()
        transcription_has_note.transcription = src
        transcription_has_note.transcription_id = src.id
        transcription_has_note.note = note
        transcription_has_note.ptr_start = data["ptr_start"]
        transcription_has_note.ptr_end = data["ptr_end"]
        note.transcription = [transcription_has_note]
    else:
        raise NotImplementedError

    return note


@api_bp.route("/api/<api_version>/documents/<doc_id>/transcriptions/notes", methods=["POST"])
@auth.login_required
def api_post_documents_transcription_notes(api_version, doc_id):
    """
     {
        "data": [
                {
                    "username": "Eleve1" (optionnal),
                    "note_type": 1,
                    "content": "My first transcription note",
                    "ptr_start": 1,
                    "ptr_end": 80
                },
                {
                    "username": "Eleve1" (optionnal),
                    "note_type": 1,
                    "content": "My second transcription note",
                    "ptr_start": 80,
                    "ptr_end": 96
                }
        ]
    }
    :param api_version:
    :param doc_id:
    :return:
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

            for n_data in data:

                user = get_current_user()
                user_id = user.id
                # teachers and admins can put/post/delete on others behalf
                if (user.is_teacher or user.is_admin) and "username" in n_data:
                    usr = get_user_from_username(n_data["username"])
                    if usr is not None:
                        user_id = usr.id

                # on wich transcription should the note be attached ?
                if (user.is_teacher or user.is_admin) and "transcription_username" in n_data:
                    tr_usr = get_user_from_username(n_data["transcription_username"])
                else:
                    tr_usr = user
                src = Transcription.query.filter(Transcription.user_id == tr_usr.id, Transcription.doc_id == doc_id).first()

                new_note = make_note_from_data(user_id, n_data, src)
                if new_note is not None:
                    db.session.add(new_note)
                    created_users.add(tr_usr)
                else:
                    raise NotImplementedError

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot insert data", "details": str(e)
                })

            if response is None:
                created_data = []
                for tr_usr in created_users:
                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            "api_bp.api_documents_transcriptions_notes",
                            api_version=api_version,
                            doc_id=doc_id,
                        ),
                        user=tr_usr
                    )
                    created_data.append(json_obj)

                response = APIResponseFactory.make_response(data=created_data)

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
