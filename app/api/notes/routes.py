
from flask import request
from sqlalchemy.orm.exc import NoResultFound

from app.api.response import APIResponseFactory
from app.api.routes import api_bp
from app.models import Transcription, Commentary, Translation, Note, NoteType


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


@api_bp.route("/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id>")
def api_documents_notes_from_user(api_version, doc_id, user_id):
    # sélectionner la liste des notes d'un utilisateur pour un doc
    # cad ses notes de transcrition, traduction, commentaire
    # TODO refactor
    """

    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    try:
        transcription = Transcription.query.filter(Transcription.doc_id == doc_id,
                                                   Transcription.user_id == user_id).first()
        translation = Translation.query.filter(Translation.doc_id == doc_id, Translation.user_id == user_id).first()
        commentaries = Commentary.query.filter(Commentary.doc_id == doc_id, Commentary.user_id == user_id).all()

        notes = []

        for it in transcription.notes:
            notes.append(it.note_id)

        for it in translation.notes:
            notes.append(it.note_id)

        for c in commentaries:
            for it in c.notes:
                notes.append(it.note_id)

        notes = Note.query.filter(Note.id.in_(notes))

        response = APIResponseFactory.make_response(data={
            'notes': [it.serialize() for it in notes]
        })
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Types de note introuvables"
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

