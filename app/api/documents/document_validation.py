from flask import current_app

from app import auth, api_bp, db
from app.models import VALIDATION_NONE, VALIDATION_TRANSCRIPTION, get_stage, VALIDATIONS_STEPS_LABELS, Document, \
    VALIDATION_TRANSLATION, VALIDATION_COMMENTARIES, VALIDATION_FACSIMILE, VALIDATION_SPEECHPARTS
from app.utils import make_200, make_400, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_404


def set_document_validation_stage(doc_id, stage_id=VALIDATION_NONE):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    user = current_app.get_current_user()
    is_another_teacher = user.is_teacher and doc.user_id != user.id

    access_forbidden = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, doc.user_id)
    if access_forbidden or is_another_teacher:
        return access_forbidden

    try:
        if stage_id not in VALIDATIONS_STEPS_LABELS.keys():
            return make_400("Invalid step id")

        doc.validation_stage = stage_id
        db.session.commit()
        return make_200(data={
            "id": doc.id,
            "validation_stage": doc.validation_stage,
            "validation_stage_label": get_stage(doc.validation_stage)
        })
    except Exception as e:
        return make_400(str(e))


# TRANSCRIPTION STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-transcription')
@auth.login_required
def api_documents_validate_transcription(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_TRANSCRIPTION)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-transcription')
@auth.login_required
def api_documents_unvalidate_transcription(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_NONE)  # previous step


# TRANSLATION STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-translation')
@auth.login_required
def api_documents_validate_translation(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_TRANSLATION)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-translation')
@auth.login_required
def api_documents_unvalidate_translation(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_TRANSCRIPTION)  # previous step


# COMMENTARIES STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-commentaries')
@auth.login_required
def api_documents_validate_commentaries(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_COMMENTARIES)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-translation')
@auth.login_required
def api_documents_unvalidate_commentaries(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_TRANSLATION)  # previous step


# FACSIMILE STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-facsimile')
@auth.login_required
def api_documents_validate_facsimile(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_FACSIMILE)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-translation')
@auth.login_required
def api_documents_unvalidate_facsimile(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_COMMENTARIES)  # previous step


# SPEECH PARTS STEP
@api_bp.route('/api/<api_version>/documents/<doc_id>/validate-speech-parts')
@auth.login_required
def api_documents_validate_speech_parts(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_SPEECHPARTS)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unvalidate-speech-parts')
@auth.login_required
def api_documents_unvalidate_speech_parts(api_version, doc_id):
    return set_document_validation_stage(doc_id=doc_id, stage_id=VALIDATION_FACSIMILE)  # previous step
