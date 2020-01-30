from flask import current_app
from flask_jwt_extended import jwt_required

from app import api_bp, db
from app.models import Document, Translation, Commentary, Transcription
from app.utils import make_200, make_400, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_404, \
    forbid_if_nor_teacher_nor_admin, make_403


def unvalidate_all(doc):
    doc.is_transcription_validated = False
    doc.is_translation_validated = False
    doc.is_facsimile_validated = False
    doc.is_speechparts_validated = False
    doc.is_commentaries_validated = False
    return doc

def commit_document_validation(doc):
    user = current_app.get_current_user()
    is_another_teacher = user.is_teacher and doc.user_id != user.id

    access_forbidden = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, doc.user_id)
    if access_forbidden or is_another_teacher:
        db.session.rollback()
        return access_forbidden

    try:
        db.session.add(doc)
        db.session.commit()
        return make_200(data=doc.validation_flags)
    except Exception as e:
        db.session.rollback()
        print(e)
        return make_400(str(e))


# GET FLAGS
@api_bp.route('/api/<api_version>/documents/<doc_id>/validation-flags')
def api_documents_get_validation_flags(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()
    return make_200(data=doc.validation_flags)


# NONE STEP (helper route)
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-none')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_validate_none(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()
    doc = unvalidate_all(doc)
    return commit_document_validation(doc)


# TRANSCRIPTION STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-transcription')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_validate_transcription(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()

    doc.is_transcription_validated = True
    return commit_document_validation(doc)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-transcription')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_unvalidate_transcription(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    doc.is_transcription_validated = False
    doc.is_translation_validated = False
    doc.is_facsimile_validated = False
    doc.is_speechparts_validated = False
    doc.is_commentaries_validated = False
    return commit_document_validation(doc)


# TRANSLATION STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-translation')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_validate_translation(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Translation.query.filter(Translation.doc_id == doc_id,
                                               Translation.user_id == doc.user_id).first() is None:
        return make_404()
    if not doc.is_transcription_validated:
        return make_403()

    doc.is_translation_validated = True
    return commit_document_validation(doc)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-translation')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_unvalidate_translation(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Translation.query.filter(Translation.doc_id == doc_id,
                                               Translation.user_id == doc.user_id).first() is None:
        return make_404()
    if not doc.is_transcription_validated:
        return make_403()
    doc.is_translation_validated = False
    return commit_document_validation(doc)


# COMMENTARIES STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-commentaries')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_validate_commentaries(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Commentary.query.filter(Commentary.doc_id == doc_id,
                                              Commentary.user_id == doc.user_id).first() is None:
        return make_404()
    if not doc.is_transcription_validated:
        return make_403()

    doc.is_commentaries_validated = True
    return commit_document_validation(doc)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-commentaries')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_unvalidate_commentaries(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Commentary.query.filter(Commentary.doc_id == doc_id,
                                              Commentary.user_id == doc.user_id).first() is None:
        return make_404()
    if not doc.is_transcription_validated:
        return make_403()

    doc.is_commentaries_validated = False
    return commit_document_validation(doc)


# FACSIMILE STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-facsimile')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_validate_facsimile(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    if not doc.is_transcription_validated:
        return make_403()
    doc.is_facsimile_validated = True
    return commit_document_validation(doc)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-facsimile')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_unvalidate_facsimile(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    if not doc.is_transcription_validated:
        return make_403()
    doc.is_facsimile_validated = False
    return commit_document_validation(doc)


# SPEECH PARTS STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-speech-parts')
@jwt_required
def api_documents_validate_speech_parts(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    if not doc.is_transcription_validated:
        return make_403()
    doc.is_speechparts_validated = True
    return commit_document_validation(doc)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-speech-parts')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_unvalidate_speech_parts(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    if not doc.is_transcription_validated:
        return make_403()
    doc.is_speechparts_validated = False
    return commit_document_validation(doc)
