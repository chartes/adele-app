from itertools import zip_longest
import re

from flask import current_app, request
from flask_jwt_extended import jwt_required
from markupsafe import Markup
from bs4 import BeautifulSoup

from app import auth, db, api_bp
from app.api.transcriptions.routes import get_reference_transcription, add_notes_refs_to_text, ETAG, BTAG
from app.api.translations.routes import get_reference_translation
from app.models import AlignmentTranslation, Transcription, Document, Translation
from app.utils import forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_404, make_200, make_400, \
    forbid_if_not_in_whitelist


SEGMENT_REGEX = re.compile('<\W*adele-segment\W*>\W*<\/\W*adele-segment\W*>')


def _build_segment(str_segment, tags_to_reopen, tags_to_close):
    segment_parts = []
    for tag in tags_to_reopen:
        segment_parts.append(f"<{tag['name']}")
        for name, value in tag["attr"].items():
            segment_parts.append(f' {name}="{value}"')
        segment_parts.append(">")
    segment_parts.append(str_segment)
    for tag in tags_to_close:
        segment_parts.append(f"</{tag['name']}>")
    return "".join(segment_parts)


def split_segments(html):
    dom = BeautifulSoup(html, "html.parser")
    raw_segments = SEGMENT_REGEX.split(html)
    segments = []
    tags_to_reopen = []
    for idx, segment in enumerate(dom.find_all("adele-segment")):
        encountered_tags = []
        for tag in segment.parents:
            if not tag or type(tag) == BeautifulSoup:
                continue
            encountered_tags.append(
                {
                    "name": tag.name,
                    "attr": tag.attrs,
                }
            )
        segments.append(
            # we use ::-1 to reverse the list, because what we first close will be last opened
            _build_segment(raw_segments[idx], tags_to_reopen[::-1], encountered_tags)
        )
        tags_to_reopen = encountered_tags
    segments.append(
        # we use ::-1 to reverse the list, because what we first close will be last opened
        _build_segment(raw_segments[-1], tags_to_reopen[::-1], [])
    )
    return segments


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id>')
@jwt_required
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
@jwt_required
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
@jwt_required
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


def add_notes_refs(tr, tl):
    all_al = AlignmentTranslation.query.filter(AlignmentTranslation.transcription_id == tr["id"],
                                               AlignmentTranslation.translation_id == tl["id"]).all()

    # recompute alignment ptr in two steps (transcription then translation)
    # by counting the number of notes tags in each segment
    # and eventually the presence of notes overlapping multiple segments
    def insert_notes_into_al(content, notes, get_al_start_ptr, get_al_end_ptr):
        offset = 0
        content_w_notes = []

        for num_al, al in enumerate(all_al):

            after_notes = []
            before_notes = []
            between_notes = []
            overlapping_note = None
            al_ptr_start = get_al_start_ptr(al)
            al_ptr_end = get_al_end_ptr(al)

            for note in notes:
                if int(note["ptr_start"]) < al_ptr_start and \
                        int(note["ptr_end"]) > al_ptr_end:
                    overlapping_note = note  # note englobant au moins une ligne en totalité
                elif (al_ptr_start <= int(note["ptr_start"]) <= al_ptr_end) and \
                        (al_ptr_start <= int(note["ptr_end"]) <= al_ptr_end):
                    between_notes.append(note) # note présente au sein d'un alignement
                elif int(note["ptr_start"]) <= al_ptr_end <= int(note["ptr_end"]):
                    after_notes.append(note)  # note finissant sur la ligne suivante
                elif int(note["ptr_start"]) <= al_ptr_start <= int(note["ptr_end"]):
                    before_notes.append(note)  # note commencant sur la ligne précédente

            # transcription al
            ptr_start = al_ptr_start + offset
            offset += len(ETAG) * len(before_notes)
            offset += (len(BTAG.format(1)) + len(ETAG)) * len(between_notes)
            offset += len(BTAG.format(1)) * len(after_notes)
            ptr_end = al_ptr_end + offset

            text = content[ptr_start:ptr_end]

            if overlapping_note:
                text = "{BTAG}{al}{ETAG}".format(BTAG=BTAG.format(overlapping_note["id"]), ETAG=ETAG, al=text)
            elif len(before_notes) > 0:
                current_note_id = before_notes[0]["id"]
                text = "{BTAG}{al}".format(BTAG=BTAG.format(current_note_id), al=text)
            elif len(after_notes) > 0:
                text = "{al}{ETAG}".format(ETAG=ETAG, al=text)

            content_w_notes.append(Markup(text))
        return content_w_notes

    tr_notes = tr["notes"]
    tl_notes = tl["notes"]
    tr_c = add_notes_refs_to_text(tr["content"], tr_notes)
    tl_c = add_notes_refs_to_text(tl["content"], tl_notes)

    tr_w_notes = insert_notes_into_al(tr_c, tr_notes, lambda al: al.ptr_transcription_start,
                                      lambda al: al.ptr_transcription_end)
    tl_w_notes = insert_notes_into_al(tl_c, tl_notes, lambda al: al.ptr_translation_start,
                                      lambda al: al.ptr_translation_end)

    notes = {n["id"]: n for n in tr_notes + tl_notes}
    notes = list(notes.values())

    return tr_w_notes, tl_w_notes, notes, len(all_al)

@api_bp.route('/api/<api_version>/documents/<doc_id>/view/transcription-alignment')
def view_document_translation_alignment(api_version, doc_id):
    translation = get_reference_translation(doc_id)
    transcription = get_reference_transcription(doc_id)

    if not transcription or not translation:
        return make_404()
    splitted_transcription = split_segments(transcription.content)
    splitted_translation = split_segments(translation.content)
    alignments = list(zip_longest(splitted_transcription, splitted_translation, fillvalue=''))

    if len(alignments) <= 1:
        return make_404(details="Aucun alignement")

    return make_200({
        "doc_id": doc_id,
        "alignments": alignments
    })


def clone_translation_alignments(doc_id, old_user_id, user_id):
    old_tr = Transcription.query.filter(Transcription.user_id == old_user_id,
                                    Transcription.doc_id == doc_id).first()

    old_tl = Translation.query.filter(Translation.user_id == old_user_id,
                                  Translation.doc_id == doc_id).first()

    new_tr = Transcription.query.filter(Transcription.user_id == user_id,
                                        Transcription.doc_id == doc_id).first()

    new_tl = Translation.query.filter(Translation.user_id == user_id,
                                      Translation.doc_id == doc_id).first()

    if not old_tr or not old_tl or not new_tr or not new_tl:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    # clone translation alignments
    old_alignments = AlignmentTranslation.query.filter(
        AlignmentTranslation.transcription_id == old_tr.id,
        AlignmentTranslation.translation_id == old_tl.id,
    ).all()

    new_alignments = [
        AlignmentTranslation(
            transcription_id=new_tr.id,
            translation_id=new_tl.id,
            ptr_transcription_start=ol.ptr_transcription_start,
            ptr_transcription_end=ol.ptr_transcription_end,
            ptr_translation_start=ol.ptr_translation_start,
            ptr_translation_end=ol.ptr_translation_end
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
