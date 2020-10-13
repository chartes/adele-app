from flask import request, current_app
from flask_jwt_extended import jwt_required
from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.documents.document_validation import commit_document_validation, unvalidate_all
from app.api.routes import api_bp
from app.models import Transcription, User, Document, AlignmentDiscours, \
    Note, TranscriptionHasNote, TranslationHasNote, Translation, findNoteInDoc
from app.utils import make_404, make_200, forbid_if_nor_teacher_nor_admin_and_wants_user_data, \
    forbid_if_nor_teacher_nor_admin, make_400, forbid_if_not_in_whitelist, is_closed, forbid_if_validation_step, \
    forbid_if_other_user, make_403, get_doc, check_no_XMLParserError

"""
===========================
    Transcriptions
===========================
"""


def get_transcription(doc_id, user_id):
    return Transcription.query.filter(
        doc_id == Transcription.doc_id,
        user_id == Transcription.user_id
    ).first()


def get_reference_transcription(doc_id):
    """

    :param doc_id:
    :return:
    """
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is not None and doc.is_transcription_validated:
        return Transcription.query.filter(
            doc_id == Transcription.doc_id,
            doc.user_id == Transcription.user_id
        ).first()

    return None

@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/users')
def api_documents_transcriptions_users(api_version, doc_id):
    users = []
    try:
        transcriptions = Transcription.query.filter(Transcription.doc_id == doc_id).all()
        users = User.query.filter(User.id.in_(set([tr.user_id for tr in transcriptions]))).all()
        users = [{"id": user.id, "username": user.username} for user in users]
    except NoResultFound:
        pass
    return make_200(data=users)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions')
def api_documents_transcriptions(api_version, doc_id):
    tr = get_reference_transcription(doc_id)
    if tr is None:
        return make_404()
    return make_200(data=tr.serialize_for_user(tr.user_id))


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>')
@jwt_required
def api_documents_transcriptions_from_user(api_version, doc_id, user_id=None):
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid
    tr = get_transcription(doc_id, user_id)
    if tr is None:
        return make_404()
    return make_200(data=tr.serialize_for_user(user_id))


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["POST"])
@jwt_required
def api_post_documents_transcriptions(api_version, doc_id, user_id):
    """
    at least one of "content" or "notes" is required
    {
        "data":
            {
                "content" :  "My first transcription"
                "notes": [
                        {
                           "content": "note1 content",
                           "ptr_start": 5,
                           "ptr_end": 7
                       }
                ]
            }
    }
    :param user_id:
    :param api_version:
    :param doc_id:
    :return:
    """
    forbid = forbid_if_other_user(current_app, user_id)
    if forbid:
        return forbid

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    # teachers can still post notes in validated transcription
    current_user = current_app.get_current_user()
    if not current_user.is_teacher and get_doc(doc_id).is_transcription_validated:
        return make_403()

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    data = request.get_json()
    if "data" in data:
        data = data["data"]
        try:
            tr = None
            # case 1) "content" in data
            if "content" in data:
                error = check_no_XMLParserError(data["content"])
                if error:
                    raise Exception('Transcription content is malformed: %s', str(error))
                tr = Transcription(doc_id=doc_id, content=data["content"], user_id=user_id)
                db.session.add(tr)
                db.session.flush()
            # case 2) there's "notes" in data
            if "notes" in data:
                tr = Transcription.query.filter(Transcription.doc_id == doc_id,
                                                Transcription.user_id == user_id).first()
            if tr is None:
                return make_404()

            if "notes" in data:
                print("======= notes =======")
                for note in data["notes"]:
                        # 1) simply reuse notes which come with an id
                    note_id = note.get('id', None)
                    if note_id is not None:
                        reused_note = Note.query.filter(Note.id == note_id, Note.user_id == current_user.id).first()
                        if reused_note is None:
                            return make_400(details="Wrong note id %s" % note_id)
                        db.session.add(reused_note)
                        db.session.flush()
                        thn = TranscriptionHasNote.query.filter(TranscriptionHasNote.note_id == reused_note.id,
                                                                TranscriptionHasNote.transcription_id == tr.id).first()
                        # 1.a) the note is already present in the transcription, so update its ptrs
                        if thn is not None:
                            raise Exception("Transcription note already exists. Consider using PUT method")
                        else:
                            # 1.b) the note is not present on the transcription side, so create it
                            thn = TranscriptionHasNote(transcription_id=tr.id,
                                                       note_id=reused_note.id,
                                                       ptr_start=note["ptr_start"],
                                                       ptr_end=note["ptr_end"])
                        db.session.add(thn)
                        print("reuse:", thn.transcription_id, thn.note_id)
                    else:
                        # 2) make new note
                        error = check_no_XMLParserError(note["content"])
                        if error:
                            raise Exception('Note content is malformed: %s', str(error))
                        new_note = Note(type_id=note.get("type_id", 0), user_id=user_id, content=note["content"])
                        db.session.add(new_note)
                        db.session.flush()
                        thn = TranscriptionHasNote(transcription_id=tr.id,
                                                   note_id=new_note.id,
                                                   ptr_start=note["ptr_start"],
                                                   ptr_end=note["ptr_end"])
                        db.session.add(thn)
                        print("make:", thn.transcription_id, thn.note_id)
                db.session.flush()
                print("thn:", [thn.note.id for thn in tr.transcription_has_note])
                print("====================")
            db.session.add(tr)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Error", str(e))
            return make_400(str(e))

        return make_200(data=tr.serialize_for_user(user_id))
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["PUT"])
@jwt_required
def api_put_documents_transcriptions(api_version, doc_id, user_id):
    """
     {
         "data":
             {
                 "content" :  "My first transcription"
                 "notes": [{
                    "id": 1,
                    "type_id": 0 (by default),
                    "content": "aaa",
                    "ptr_start": 3,
                    "ptr_end": 12
                 }]
             }
     }
     :param user_id:
     :param api_version:
     :param doc_id:
     :return:
     """
    forbid = forbid_if_other_user(current_app, user_id)
    if forbid:
        return forbid

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    # teachers can still update validated transcription
    current_user = current_app.get_current_user()
    if not current_user.is_teacher and get_doc(doc_id).is_transcription_validated:
        return make_403()

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    data = request.get_json()
    if "data" in data:
        data = data["data"]
        tr = get_transcription(doc_id=doc_id, user_id=user_id)
        if tr is None:
            return make_404()
        try:
            if "content" in data:
                error = check_no_XMLParserError(data["content"])
                if error:
                    raise Exception('Transcription content is malformed: %s', str(error))
                tr.content = data["content"]
                db.session.add(tr)
                db.session.commit()
            if "notes" in data:
                current_transcription_notes = TranscriptionHasNote.query.filter(
                    TranscriptionHasNote.transcription_id == tr.id).all()
                # remove all notes not present in the transcription anymore
                for current_thn in current_transcription_notes:
                    if (current_thn.note.id, current_thn.ptr_start, current_thn.ptr_end) not in \
                            [(note.get('id', None), note["ptr_start"], note["ptr_end"])
                             for note in data["notes"]]:
                        note = current_thn.note
                        db.session.delete(current_thn)
                        print("delete thn", note)
                        db.session.flush()
                        note.delete_if_unused()


                for note in data["notes"]:
                    note_id = note.get('id', None)
                    thn = TranscriptionHasNote.query.filter(
                        TranscriptionHasNote.note_id == note_id,
                        TranscriptionHasNote.transcription_id == tr.id,
                        TranscriptionHasNote.ptr_start == note["ptr_start"],
                        TranscriptionHasNote.ptr_end == note["ptr_end"]
                    ).first()
                    if thn is None:
                        # try to find the note in other contents
                        reused_note = findNoteInDoc(doc_id, user_id, note_id)
                        if reused_note is None:
                            raise Exception('Cannot reuse note: note %s unknown' % note_id)

                        # bind the note on the transcription side
                        thn = TranscriptionHasNote(transcription_id=tr.id,
                                                       note_id=reused_note.id,
                                                       ptr_start=note["ptr_start"],
                                                       ptr_end=note["ptr_end"])
                        db.session.add(thn)
                        db.session.flush()

                    error = check_no_XMLParserError(note["content"])
                    if error:
                        raise Exception('Note content is malformed: %s', str(error))

                    thn.ptr_start = note['ptr_start']
                    thn.ptr_end = note['ptr_end']
                    thn.note.content = note['content']
                    thn.note.type_id = note['type_id']

                    db.session.add(thn)
                    db.session.add(thn.note)

                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Error', str(e))
            return make_400(str(e))
        return make_200(data=tr.serialize_for_user(user_id))
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["DELETE"])
@jwt_required
def api_delete_documents_transcriptions(api_version, doc_id, user_id):
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    closed = is_closed(doc_id)
    if closed:
        return closed

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed

    # forbid students to delete a transcription when there is a valid transcription
    #user = current_app.get_current_user()
    #if not user.is_teacher and get_doc(doc_id).is_transcription_validated:
    #    return make_403()

    tr = get_transcription(doc_id=doc_id, user_id=user_id)
    if tr is None:
        return make_404()

    try:
        for thn in tr.transcription_has_note:
            if thn.note.user_id == int(user_id):
                exist_in_translation = TranslationHasNote.query.filter(
                    TranslationHasNote.note_id == thn.note.id
                ).first()
                if not exist_in_translation:
                    db.session.delete(thn.note)
        db.session.delete(tr)
        doc = unvalidate_all(doc)
        db.session.add(doc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200(data=doc.validation_flags)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/clone/from-user/<user_id>', methods=['GET'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_clone_transcription(api_version, doc_id, user_id):
    print("cloning transcription (doc %s) from user %s" % (doc_id, user_id))

    tr_to_be_cloned = Transcription.query.filter(Transcription.user_id == user_id,
                                                 Transcription.doc_id == doc_id).first()

    if not tr_to_be_cloned:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    teacher = current_app.get_current_user()
    teacher_tr = Transcription.query.filter(Transcription.user_id == teacher.id,
                                            Transcription.doc_id == doc_id).first()
    if teacher_tr is None:
        teacher_tr = Transcription(doc_id=doc_id, user_id=teacher.id, content=tr_to_be_cloned.content)
    else:
        # replace the teacher's tr content
        teacher_tr.content = tr_to_be_cloned.content
        # remove the old teacher's notes
        for note in teacher_tr.notes:
            db.session.delete(note)
        #teacher_tr.notes = []

    # clone notes
    for thn_to_be_cloned in tr_to_be_cloned.transcription_has_note:
        note = Note(type_id=thn_to_be_cloned.note.type_id, user_id=teacher.id,
                    content=thn_to_be_cloned.note.content)
        db.session.add(note)
        db.session.flush()
        teacher_tr.transcription_has_note.append(
            TranscriptionHasNote(ptr_start=thn_to_be_cloned.ptr_start,
                                 ptr_end=thn_to_be_cloned.ptr_end,
                                 note_id=note.id,
                                 transcription_id=teacher_tr.id),
        )

    db.session.add(teacher_tr)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200()


# tags to represent notes in view mode
BTAG = "<span class='note-placeholder' data-note-id='{:010d}'>"
ETAG = "</span>"


def _ptr_start(k):
    return k["ptr_start"]


def add_notes_refs_to_text(text, notes, btag=BTAG, etag=ETAG):
    len_of_tag = len(btag) + len(etag)
    text_with_notes = text

    notes.sort(key=_ptr_start)
    for num_note, note in enumerate(notes):
        offset = len_of_tag * num_note
        offset += 3 * num_note  # decalage?
        start_offset = int(note["ptr_start"]) + offset
        end_offset = int(note["ptr_end"]) + offset
        kwargs = {
            "btag": btag.format(note["id"]),
            "etag": etag,
            "text_before": text_with_notes[0:start_offset],
            "text_between": text_with_notes[start_offset:end_offset],
            "text_after": text_with_notes[end_offset:]
        }
        text_with_notes = "{text_before}{btag}{text_between}{etag}{text_after}".format(**kwargs)
    return text_with_notes


@api_bp.route('/api/<api_version>/documents/<doc_id>/view/transcriptions')
@api_bp.route('/api/<api_version>/documents/<doc_id>/view/transcriptions/from-user/<user_id>')
def view_document_transcription(api_version, doc_id, user_id=None):
    if user_id is not None:
        forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
        if forbid:
            return forbid
        tr = get_transcription(doc_id, user_id)
    else:
        tr = get_reference_transcription(doc_id)

    if tr is None:
        return make_404()

    if user_id is None:
        user_id = tr.user_id

    _tr = tr.serialize_for_user(user_id)
    _content = add_notes_refs_to_text(_tr["content"], _tr["notes"])

    return make_200({
        "doc_id": tr.doc_id,
        "user_id": tr.user_id,
        "content": Markup(_content) if tr.content is not None else "",
        "notes": {"{:010d}".format(n["id"]): n["content"] for n in _tr["notes"]}
    })
