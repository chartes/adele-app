from flask import current_app, request

from app import auth, db, api_bp
from app.models import AlignmentTranslation
from app.utils import forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_404, make_200, make_400


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id>')
@auth.login_required
def api_get_alignment_translation_from_user(api_version, doc_id, user_id):
    from app.api.transcriptions.routes import get_reference_transcription
    from app.api.translations.routes import get_translation

    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return make_404(details="No transcription available")

    translation = get_translation(doc_id=doc_id, user_id=user_id)
    if translation is None:
        return make_404(details="No translation available")

    alignments = AlignmentTranslation.query.filter(
        AlignmentTranslation.transcription_id == transcription.id,
        AlignmentTranslation.translation_id == translation.id
    ).all()

    ptrs = [(a.ptr_transcription_start, a.ptr_transcription_end,
             a.ptr_translation_start, a.ptr_translation_end)
            for a in alignments]

    return make_200(data=ptrs)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments')
def api_get_alignment_translation(api_version, doc_id):
    from app.api.transcriptions.routes import get_reference_transcription
    from app.api.translations.routes import get_reference_translation

    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return make_404(details="No transcription available")

    translation = get_reference_translation(doc_id)
    if translation is None:
        return make_404(details="No translation available")

    alignments = AlignmentTranslation.query.filter(
        AlignmentTranslation.transcription_id == transcription.id,
        AlignmentTranslation.translation_id == translation.id
    ).all()

    ptrs = [(a.ptr_transcription_start, a.ptr_transcription_end,
             a.ptr_translation_start, a.ptr_translation_end)
            for a in alignments]

    return make_200(data=ptrs)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id>', methods=['POST'])
@auth.login_required
def api_post_translation_alignments(api_version, doc_id, user_id):
    """
        NB: Posting alignment has a 'TRUNCATE AND REPLACE' effect
    """
    from app.api.transcriptions.routes import get_reference_transcription
    from app.api.translations.routes import get_translation

    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return make_404(details="Transcription not found")

    translation = get_translation(doc_id=doc_id, user_id=user_id)
    if translation is None:
        return make_404(details="Translation not found")

    data = request.get_json()
    data = data.get("data", [])
    ptrs = []
    try:
        # TRUNCATE
        for old_al in AlignmentTranslation.query.filter(
                AlignmentTranslation.transcription_id == transcription.id,
                AlignmentTranslation.translation_id == translation.id
        ).all():
            db.session.delete(old_al)

        # INSERT
        for (ptr_transcription_start, ptr_transcription_end,
             ptr_translation_start, ptr_translation_end) in data:
            new_al = AlignmentTranslation(
                transcription_id=transcription.id,
                translation_id=translation.id,
                ptr_transcription_start=ptr_transcription_start,
                ptr_transcription_end=ptr_transcription_end,
                ptr_translation_start=ptr_translation_start,
                ptr_translation_end=ptr_translation_end
            )
            db.session.add(new_al)
            ptrs.append((new_al.ptr_transcription_start, new_al.ptr_transcription_end,
                         new_al.ptr_translation_start, new_al.ptr_translation_end))

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200(data=ptrs)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id>', methods=['DELETE'])
@auth.login_required
def api_delete_translation_alignments(api_version, doc_id, user_id):
    from app.api.transcriptions.routes import get_reference_transcription
    from app.api.translations.routes import get_translation

    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return make_404(details="Transcription not found")

    translation = get_translation(doc_id=doc_id, user_id=user_id)
    if translation is None:
        return make_404(details="Translation not found")

    try:
        # TRUNCATE
        for old_al in AlignmentTranslation.query.filter(
                AlignmentTranslation.transcription_id == transcription.id,
                AlignmentTranslation.translation_id == translation.id
        ).all():
            db.session.delete(old_al)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200(data=[])
