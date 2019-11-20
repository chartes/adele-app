from flask import current_app
from flask_jwt_extended import jwt_required

from app import auth, api_bp, db
from app.models import VALIDATION_NONE, VALIDATION_TRANSCRIPTION, get_validation_step_label, VALIDATIONS_STEPS_LABELS, \
    Document, \
    VALIDATION_TRANSLATION, VALIDATION_COMMENTARIES, VALIDATION_FACSIMILE, VALIDATION_SPEECHPARTS, Transcription, \
    Translation, Commentary, AlignmentImage
from app.utils import make_200, make_400, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_404


def set_document_validation_step(doc, stage_id=VALIDATION_NONE):
    user = current_app.get_current_user()
    is_another_teacher = user.is_teacher and doc.user_id != user.id

    access_forbidden = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, doc.user_id)
    if access_forbidden or is_another_teacher:
        return access_forbidden

    try:
        if stage_id not in VALIDATIONS_STEPS_LABELS.keys():
            return make_400("Invalid step id")

        doc.validation_step = stage_id
        db.session.commit()
        return make_200(data={
            "id": doc.id,
            "validation_step": doc.validation_step,
            "validation_step_label": get_validation_step_label(doc.validation_step)
        })
    except Exception as e:
        return make_400(str(e))


# TRANSCRIPTION STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-transcription')
@jwt_required
def api_documents_validate_transcription(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id, Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_TRANSCRIPTION)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-transcription')
@jwt_required
def api_documents_unvalidate_transcription(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_NONE)  # previous step


# TRANSLATION STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-translation')
@jwt_required
def api_documents_validate_translation(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Translation.query.filter(Translation.doc_id == doc_id,
                                               Translation.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_TRANSLATION)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-translation')
@jwt_required
def api_documents_unvalidate_translation(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Translation.query.filter(Translation.doc_id == doc_id,
                                               Translation.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_TRANSCRIPTION)  # previous step


# COMMENTARIES STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-commentaries')
@jwt_required
def api_documents_validate_commentaries(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Commentary.query.filter(Commentary.doc_id == doc_id,
                                              Commentary.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_COMMENTARIES)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-commentaries')
@jwt_required
def api_documents_unvalidate_commentaries(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Commentary.query.filter(Commentary.doc_id == doc_id,
                                              Commentary.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_TRANSLATION)  # previous step


# FACSIMILE STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-facsimile')
@jwt_required
def api_documents_validate_facsimile(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_FACSIMILE)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-facsimile')
@jwt_required
def api_documents_unvalidate_facsimile(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_COMMENTARIES)  # previous step


# SPEECH PARTS STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-speech-parts')
@jwt_required
def api_documents_validate_speech_parts(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_SPEECHPARTS)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-speech-parts')
@jwt_required
def api_documents_unvalidate_speech_parts(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None or Transcription.query.filter(Transcription.doc_id == doc_id,
                                                 Transcription.user_id == doc.user_id).first() is None:
        return make_404()
    return set_document_validation_step(doc=doc, stage_id=VALIDATION_FACSIMILE)  # previous step
