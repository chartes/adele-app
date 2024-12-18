from flask import request, current_app
from flask_jwt_extended import jwt_required
from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import make_transient

from app import db
from app.api.documents.document_validation import unvalidate_all
from app.api.routes import api_bp
from app.models import Transcription, User, Document, \
    Note, TranscriptionHasNote, TranslationHasNote, findNoteInDoc, set_notes_from_content
from app.utils import make_404, make_200, forbid_if_nor_teacher_nor_admin_and_wants_user_data, \
    forbid_if_nor_teacher_nor_admin, make_400, forbid_if_not_in_whitelist, is_closed, \
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
    #forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    #if forbid:
    #    return forbid
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
            }
    }
    :param user_id:
    :param api_version:
    :param doc_id:
    :return:
    """
    #forbid = forbid_if_other_user(current_app, user_id)
    #if forbid:
    #    return forbid

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
            error = check_no_XMLParserError(data["content"])
            if error:
                raise Exception('Transcription content is malformed: %s', str(error))
            tr = Transcription(doc_id=doc_id, content=data["content"], user_id=user_id)
            set_notes_from_content(tr)
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
             }
     }
     :param user_id:
     :param api_version:
     :param doc_id:
     :return:
     """
    #forbid = forbid_if_other_user(current_app, user_id)
    #if forbid:
    #    return forbid

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
        transcription = get_transcription(doc_id=doc_id, user_id=user_id)
        if transcription is None:
            return make_404()
        try:
                error = check_no_XMLParserError(data["content"])
                if error:
                    raise Exception('Transcription content is malformed: %s', str(error))
                transcription.content = data["content"]
                notes = set(transcription.notes)
                set_notes_from_content(transcription)
                db.session.flush()
                for note in notes:
                    note.delete_if_unused()
                db.session.add(transcription)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Error', str(e))
            return make_400(str(e))
        return make_200(data=transcription.serialize_for_user(user_id))
    else:
        return make_400("no data")


def delete_document_transcription(doc_id, user_id):
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
    # user = current_app.get_current_user()
    # if not user.is_teacher and get_doc(doc_id).is_transcription_validated:
    #    return make_403()

    tr = get_transcription(doc_id=doc_id, user_id=user_id)
    #print("delete_document_transcription / doc_id / user_id", tr, doc_id, user_id)
    if tr is None:
        return make_404()

    try:
        db.session.delete(tr)
        doc = unvalidate_all(doc)
        db.session.add(doc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200(data=doc.validation_flags)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["DELETE"])
@jwt_required
def api_delete_documents_transcriptions(api_version, doc_id, user_id):
    return delete_document_transcription(doc_id, user_id)

def clone_transcription(doc_id, user_id):
    print("cloning transcription (doc %s) from user %s" % (doc_id, user_id))

    tr_to_be_cloned = Transcription.query.filter(Transcription.user_id == user_id,
                                                 Transcription.doc_id == doc_id).first()

    if not tr_to_be_cloned:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    teacher = current_app.get_current_user()
    teacher_tr = db.session.query(Transcription).filter(Transcription.user_id == teacher.id,
                                            Transcription.doc_id == doc_id).first()

    if teacher_tr is None:
        # create a transcription object with the cloned content
        teacher_tr = Transcription(doc_id=doc_id, user_id=teacher.id, content=tr_to_be_cloned.content)
        #print("cloning transcription teacher_tr id / content when None:", teacher_tr.id, teacher_tr.content)
    else:
        #print("cloning transcription teacher_tr id / content :", teacher_tr.id, teacher_tr.content)
        # remove the old teacher's transcription (its notes will be cascade deleted)
        db.session.delete(teacher_tr)
        db.session.flush()

    # make teacher_tr transient to be able to update it & allow db.session.add(teacher_tr) below
    make_transient(teacher_tr)
    # replace the teacher's transcription content TEXT
    teacher_tr.content = tr_to_be_cloned.content

    # clone new notes (! their former ids -linked to the source owner user_id- will need to replaced the in transcription)
    for note_to_be_cloned in tr_to_be_cloned.notes:
        #print("clone_transcription note_to_be_cloned / note_to_be_cloned.id : ", note_to_be_cloned, note_to_be_cloned.id)

        note = Note(type_id=note_to_be_cloned.type_id, user_id=teacher.id,
                    content=note_to_be_cloned.content)
        #print("note ", note)

        # push the note to db to obtain its id and update the note's id within the transcription content
        db.session.add(note)
        db.session.flush()
        # now the new note id for the teacher is available

        # replace the teacher's transcription content WITH NEW notes' ids (recursively using teacher_tr.content)
        teacher_tr.content = teacher_tr.content.replace(str(note_to_be_cloned.id), str(note.id))
        #print("clone_transcription replace note id in tr with current user : ", teacher_tr.content)
        #print("teacher_tr teacher_tr.notes / type(teacher_tr.notes) : ", teacher_tr, teacher_tr.notes, type(teacher_tr.notes))

        # add the notes also to the db relationships
        teacher_tr.notes.add(note)

    db.session.add(teacher_tr)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200()


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/clone/from-user/<user_id>', methods=['GET'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_clone_transcription(api_version, doc_id, user_id):
    return clone_transcription(doc_id, user_id)


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
    #    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    #    if forbid:
    #        return forbid
        tr = get_transcription(doc_id, user_id)
    else:
        tr = get_reference_transcription(doc_id)

    if tr is None:
        return make_404()

    if user_id is None:
        user_id = tr.user_id

    _tr = tr.serialize_for_user(user_id)

    return make_200({
        "doc_id": tr.doc_id,
        "user_id": tr.user_id,
        "content": Markup(_tr["content"]) if tr.content is not None else "",
        "notes": {"{:010d}".format(n["id"]): n["content"] for n in _tr["notes"]}
    })
