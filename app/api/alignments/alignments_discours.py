from flask import request, current_app
from flask_jwt_extended import jwt_required
from markupsafe import Markup

from app import api_bp, db
from app.api.transcriptions.routes import get_reference_transcription
from app.models import AlignmentDiscours, Transcription, Document
from app.utils import make_404, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_200, make_400, \
    forbid_if_not_in_whitelist


@api_bp.route('/api/<api_version>/documents/<doc_id>/speech-parts')
@api_bp.route('/api/<api_version>/documents/<doc_id>/speech-parts/from-user/<user_id>')
def api_documents_transcriptions_alignments_discours(api_version, doc_id, user_id=None):
    """
    If user_id is None: get the reference translation (if any) to find the alignment
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        return make_404()

    if user_id is None:
        user_id = transcription.user_id
    else:
        forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
        if forbid:
            return forbid

    alignments = AlignmentDiscours.query.filter(
        AlignmentDiscours.transcription_id == transcription.id,
        AlignmentDiscours.user_id == user_id
    ).all()

    if len(alignments) == 0:
        return make_404()

    return make_200(data=[al.serialize() for al in alignments])


def add_speechparts_refs_to_text(text, alignments):
    text_with_notes = text
    # tags to represent notes in view mode
    BTAG = "<span class='speech-part type-{speech_part_type_id:02d}' data-note-id='{note_id:010d}'>"
    ETAG = "</span>"

    notes = [
        {
            "id": al.id,
            "speech_part_type_id": al.speech_part_type.id,
            "ptr_start": al.ptr_start,
            "ptr_end": al.ptr_end,
            "content": al.note
        }
        for al in alignments
    ]

    def _ptr_start(k):
        return k["ptr_start"]

    notes.sort(key=_ptr_start)
    for num_note, note in enumerate(notes):

        btag = BTAG.format(speech_part_type_id=note['speech_part_type_id'], note_id=note["id"])
        len_of_tag = len(btag) + len(ETAG)

        offset = len_of_tag * num_note
        #offset += 3 * num_note  # decalage?
        start_offset = int(note["ptr_start"]) + offset
        end_offset = int(note["ptr_end"]) + offset
        kwargs = {
            "btag": btag,
            "etag": ETAG,
            "text_before": text_with_notes[0:start_offset],
            "text_between": text_with_notes[start_offset:end_offset],
            "text_after": text_with_notes[end_offset:]
        }
        text_with_notes = "{text_before}{btag}{text_between}{etag}{text_after}".format(**kwargs)
    return text_with_notes


@api_bp.route('/api/<api_version>/documents/<doc_id>/view/speech-parts')
@api_bp.route('/api/<api_version>/documents/<doc_id>/view/speech-parts/from-user/<user_id>')
def view_document_speech_parts_alignment(api_version, doc_id, user_id=None):
    tr = get_reference_transcription(doc_id)

    if tr is None:
        return make_404()

    if user_id is None:
        user_id = tr.user_id

    alignments = AlignmentDiscours.query.filter(
        AlignmentDiscours.transcription_id == tr.id,
        AlignmentDiscours.user_id == user_id
    ).all()

    if len(alignments) <= 0:
        return make_404(details="Aucun alignement")

    _content = add_speechparts_refs_to_text(tr.content, alignments)

    return make_200({
        "content": Markup(_content) if tr.content is not None else "",
        "notes": {"{:010d}".format(al.id): al.note for al in alignments}
    })


@api_bp.route('/api/<api_version>/documents/<doc_id>/speech-parts', methods=['POST'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/speech-parts/from-user/<user_id>', methods=['POST'])
@jwt_required
def api_post_documents_transcriptions_alignments_discours(api_version, doc_id, user_id):
    """
        {
            "data": [
                    {
                        "speech_part_type_id" : 1,
                        "ptr_start": 1,
                        "ptr_end": 20,
                        "note": "aaa"
                    },
                    {
                        "speech_part_type_id" : 2,
                        "ptr_start": 21,
                        "ptr_end": 450,
                        "note": "bb"
                    }
            ]
        }

        :param user_id:
        :param api_version:
        :param doc_id:
        :return:
        """
    """
           NB: Posting alignment has a 'TRUNCATE AND REPLACE' effect
       """

    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return make_404(details="Transcription not found")

    data = request.get_json()
    data = data.get("data", [])
    ptrs = []
    try:
        # TRUNCATE
        for old_al in AlignmentDiscours.query.filter(
                AlignmentDiscours.transcription_id == transcription.id,
                AlignmentDiscours.user_id == user_id
        ).all():
            db.session.delete(old_al)

        # INSERT
        for d in data:
            new_al = AlignmentDiscours(
                transcription_id=transcription.id,
                speech_part_type_id=d["speech_part_type_id"],
                ptr_start=d["ptr_start"],
                ptr_end=d["ptr_end"],
                user_id=user_id,
                note=d.get('note', None)
            )
            db.session.add(new_al)
            ptrs.append({
                         'id': new_al.id,
                         'ptr_start': new_al.ptr_start,
                         'ptr_end': new_al.ptr_end,
                         'note': new_al.note,
                         'speech_part_type_id': new_al.speech_part_type_id
                         })

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200(data=ptrs)


@api_bp.route('/api/<api_version>/documents/<doc_id>/speech-parts/from-user/<user_id>', methods=['DELETE'])
@jwt_required
def api_delete_speechparts_alignments(api_version, doc_id, user_id):
    from app.api.transcriptions.routes import get_reference_transcription

    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return make_404(details="Transcription not found")

    try:
        # TRUNCATE
        for old_al in AlignmentDiscours.query.filter(
                AlignmentDiscours.transcription_id == transcription.id,
                AlignmentDiscours.user_id == user_id
        ).all():
            db.session.delete(old_al)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200(data=[])


def clone_speechparts(doc_id, old_user_id, user_id):
    old_tr = Transcription.query.filter(Transcription.user_id == old_user_id,
                                    Transcription.doc_id == doc_id).first()

    new_tr = Transcription.query.filter(Transcription.user_id == user_id,
                                        Transcription.doc_id == doc_id).first()

    if not old_tr or not new_tr:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    # clone speechparts
    old_alignments = AlignmentDiscours.query.filter(
        AlignmentDiscours.transcription_id == old_tr.id,
        AlignmentDiscours.user_id == old_user_id,
    ).all()

    new_alignments = [
        AlignmentDiscours(
            transcription_id=new_tr.id,
            user_id=user_id,
            speech_part_type_id=ol.speech_part_type_id,
            note=ol.note,
            ptr_start=ol.ptr_start,
            ptr_end=ol.ptr_end
        )
        for ol in old_alignments
    ]

    db.session.bulk_save_objects(new_alignments)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200()
