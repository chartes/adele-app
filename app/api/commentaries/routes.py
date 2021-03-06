from flask import request, current_app
from flask_jwt_extended import jwt_required
from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound

from app import db
from app.api.routes import api_bp
from app.api.transcriptions.routes import get_reference_transcription, add_notes_refs_to_text
from app.models import Commentary, Document, Note, TranscriptionHasNote, CommentaryHasNote, Transcription, findNoteInDoc
from app.utils import make_403, make_200, make_404, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_409, \
    make_400, get_doc, is_closed, check_no_XMLParserError, forbid_if_nor_teacher_nor_admin, forbid_if_not_in_whitelist


def get_commentaries(doc_id, user_id):
    """

    :param user_id:
    :param type_id:
    :param doc_id:
    :return:
    """
    return Commentary.query.filter(
        doc_id == Commentary.doc_id,
        user_id == Commentary.user_id,
    ).all()


def get_reference_commentaries(doc_id, type_id=None):
    """

    :param type_id:
    :param doc_id:
    :return:
    """
    from app.api.transcriptions.routes import get_reference_transcription
    tr_ref = get_reference_transcription(doc_id)
    if tr_ref is None:
        return []

    if type_id is None:
        type_id = Commentary.type_id

    return Commentary.query.filter(
        doc_id == Commentary.doc_id,
        tr_ref.user_id == Commentary.user_id,
        type_id == Commentary.type_id
    ).all()


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries')
def api_all_commentary(api_version, doc_id):
    if not get_doc(doc_id).is_transcription_validated:
        return make_403()

    tr = get_reference_transcription(doc_id)
    if tr is None:
        return make_404()

    commentaries = Commentary.query.filter(
        Commentary.doc_id == doc_id,
        Commentary.user_id == tr.user_id,
    ).all()

    return make_200(data=[c.serialize() for c in commentaries])


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>')
@jwt_required
def api_commentary_from_user(api_version, doc_id, user_id):
    print(current_app.get_current_user())
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    # teachers can still post notes in validated transcription
    #current_user = current_app.get_current_user()
    #if not current_user.is_teacher and get_doc(doc_id).is_transcription_validated:
    #    return make_403()

    commentaries = Commentary.query.filter(
        Commentary.doc_id == doc_id,
        Commentary.user_id == user_id,
    ).all()

    if len(commentaries) == 0:
        return make_404()

    return make_200(data=[c.serialize() for c in commentaries])


@api_bp.route('/api/<api_version>/documents/<doc_id>/view/commentaries')
@api_bp.route('/api/<api_version>/documents/<doc_id>/view/commentaries/from-user/<user_id>')
def view_document_commentaries(api_version, doc_id, user_id=None):
    if user_id is not None:
        forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
        if forbid:
            return forbid
        coms = get_commentaries(doc_id, user_id)
    else:
        coms = get_reference_commentaries(doc_id)

    if coms is None or len(coms) == 0:
        return make_404()

    _coms = [c.serialize() for c in coms]
    _coms_content = [add_notes_refs_to_text(c["content"], c["notes"]) for c in _coms]
    commentaries = zip(_coms, _coms_content)

    return make_200(data=[{
        "doc_id": com["doc_id"],
        "user_id": com["user_id"],
        "type": com["type"],
        "content": Markup(annotated) if annotated is not None else "",
        "notes": {"{:010d}".format(n["id"]): n["content"] for n in com["notes"]}
    } for com, annotated in commentaries])


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id>',
              methods=['DELETE'])
@jwt_required
def api_delete_commentary(api_version, doc_id, user_id=None, type_id=None):
    user = current_app.get_current_user()

    # only teacher and admin can see everything
    access_is_forbidden = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if access_is_forbidden:
        return access_is_forbidden

    if not (user.is_teacher or user.is_admin) and type_id is not None and user_id is None:
        user_id = user.id

    if type_id is None:
        type_id = Commentary.type_id
    if user_id is None:
        if user.is_teacher:
            user_id = Commentary.user_id
        else:
            user_id = user.id

    commentaries = Commentary.query.filter(
        Commentary.doc_id == doc_id,
        Commentary.user_id == user_id,
        Commentary.type_id == type_id
    ).all()

    for c in commentaries:
        db.session.delete(c)

    try:
        db.session.commit()

        # change validation step

        return make_200(data={
            # "validation_step": doc.validation_step,
            # "validation_step_label": get_validation_step_label(doc.validation_step)
        })
    except (Exception, KeyError) as e:
        db.session.rollback()
        return make_400(str(e))


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>', methods=['POST'])
@jwt_required
def api_post_commentary(api_version, doc_id, user_id):
    """
    {
        "data":
            {
                "type_id": 2,
                "content" : "This is a commentary",
                "notes": [
                        {
                           "content": "note1 content",
                           "ptr_start": 5,
                           "ptr_end": 7
                       }
                ]
            }
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    doc = get_doc(doc_id)
    if doc is None:
        return make_404()

    # teachers can still post notes in if the commentaries are validated
    user = current_app.get_current_user()
    if not user.is_teacher and doc.is_commentaries_validated:
        return make_403()

    data = request.get_json()
    if "data" in data:
        data = data["data"]

        data["user_id"] = user_id # user.id

        try:
            c = None
            # case 1) "content" in data
            if "content" in data:
                error = check_no_XMLParserError(data["content"])
                if error:
                    raise Exception('Commentary content is malformed: %s', str(error))
                c = Commentary(doc_id=doc_id, user_id=user_id, type_id=data["type_id"], content=data["content"])
                db.session.add(c)
                db.session.flush()
            # case 2) there's "notes" in data
            elif "notes" in data:
                c = Commentary.query.filter(Commentary.doc_id == doc_id,
                                            Commentary.user_id == user_id,
                                            Commentary.type_id == data["type_id"]).first()

            print(doc, c, user, data)
            if c is None:
                return make_404()

            if "notes" in data:
                print("======= notes =======")
                for note in data["notes"]:
                    # 1) simply reuse notes which come with an id
                    note_id = note.get('id', None)
                    if note_id is not None:
                        reused_note = Note.query.filter(Note.id == note_id, Note.user_id == user_id).first()
                        if reused_note is None:
                            return make_400(details="Wrong note id %s" % note_id)
                        db.session.add(reused_note)
                        db.session.flush()
                        chn = CommentaryHasNote.query.filter(CommentaryHasNote.note_id == reused_note.id,
                                                             CommentaryHasNote.commentary_id == c.id).first()
                        # 1.a) the note is already present in the commentary, so update its ptrs
                        if chn is not None:
                            raise Exception("Commentary note already exists. Consider using PUT method")
                        else:
                            # 1.b) the note is not present on the transcription side, so create it
                            chn = CommentaryHasNote(commentary_id=c.id,
                                                    note_id=reused_note.id,
                                                    ptr_start=note["ptr_start"],
                                                    ptr_end=note["ptr_end"])
                        db.session.add(chn)
                        print("reuse:", chn.transcription_id, chn.note_id)
                    else:
                        # 2) make new note
                        error = check_no_XMLParserError(note["content"])
                        if error:
                            raise Exception('Note content is malformed: %s', str(error))
                        new_note = Note(type_id=note.get("type_id", 0), user_id=user_id, content=note["content"])
                        db.session.add(new_note)
                        db.session.flush()
                        chn = CommentaryHasNote(commentary_id=c.id,
                                                note_id=new_note.id,
                                                ptr_start=note["ptr_start"],
                                                ptr_end=note["ptr_end"])
                        db.session.add(chn)
                        print("make:", chn.commentary_id, chn.note_id)
                    db.session.flush()
                    print("====================")
                    db.session.add(chn)
            db.session.commit()

        except (Exception, KeyError) as e:
            db.session.rollback()
            print(str(e))
            return make_400(str(e))

        return make_200(c.serialize())
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>', methods=['PUT'])
@jwt_required
def api_put_commentary(api_version, doc_id, user_id):
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
        :param api_version:
        :param doc_id:
        :return:
        """
    doc = get_doc(doc_id)
    # teachers can still post notes in if the commentaries are validated
    current_user = current_app.get_current_user()
    if not current_user.is_teacher and doc.is_commentaries_validated:
        return make_403()

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    data = request.get_json()
    if "data" in data:
        data = data["data"]
        c = Commentary.query.filter(
            data["type_id"] == Commentary.type_id,
            doc_id == Commentary.doc_id,
            user_id == Commentary.user_id,
        ).first()

        if c is None:
            return make_404()

        try:
            if "content" in data:
                error = check_no_XMLParserError(data["content"])
                if error:
                    raise Exception('Commentary content is malformed: %s', str(error))
                c.content = data["content"]
                db.session.add(c)
                db.session.commit()
            if "notes" in data:

                current_commentary_notes = CommentaryHasNote.query.filter(CommentaryHasNote.commentary_id == c.id).all()
                # remove all notes not present in the transcription anymore
                for current_chn in current_commentary_notes:
                    if (current_chn.note.id, current_chn.ptr_start, current_chn.ptr_end) not in \
                            [(note.get('id', None), note["ptr_start"], note["ptr_end"])
                             for note in data["notes"]]:
                        note = current_chn.note
                        db.session.delete(current_chn)
                        print("delete chn", note)
                        db.session.flush()
                        note.delete_if_unused()

                for note in data["notes"]:

                    note_id = note.get('id', None)
                    chn = CommentaryHasNote.query.filter(CommentaryHasNote.note_id == note_id,
                                                         CommentaryHasNote.commentary_id == c.id,
                                                         CommentaryHasNote.ptr_start == note["ptr_start"],
                                                         CommentaryHasNote.ptr_end == note["ptr_end"]
                                                         ).first()
                    if chn is None:
                        # try to find a note in other contents
                        reused_note = findNoteInDoc(doc_id, user_id, note_id)
                        if reused_note is None:
                            raise Exception('Cannot reuse note: note %s unknown' % note_id)
                        chn = CommentaryHasNote(commentary_id=c.id,
                                                note_id=reused_note.id,
                                                ptr_start=note["ptr_start"],
                                                ptr_end=note["ptr_end"])
                        db.session.add(chn)
                        db.session.flush()

                    error = check_no_XMLParserError(note["content"])
                    if error:
                        raise Exception('Note content is malformed: %s', str(error))

                    chn.ptr_start = note['ptr_start']
                    chn.ptr_end = note['ptr_end']
                    chn.note.content = note['content']
                    chn.note.type_id = note['type_id']

                    db.session.add(chn)
                    db.session.add(chn.note)

                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Error', str(e))
            return make_400(str(e))
        return make_200(data=c.serialize())
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/clone/from-user/<user_id>/and-type/<type_id>',
              methods=['GET'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_clone_commentary(api_version, doc_id, user_id, type_id):
    com_to_be_cloned = Commentary.query.filter(Commentary.user_id == user_id,
                                               Commentary.doc_id == doc_id,
                                               Commentary.type_id == type_id).first()
    if not com_to_be_cloned:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    teacher = current_app.get_current_user()
    teacher_com = Commentary.query.filter(Commentary.user_id == teacher.id,
                                          Commentary.type_id == type_id,
                                          Commentary.doc_id == doc_id).first()
    if teacher_com is None:
        teacher_com = Commentary(doc_id=doc_id, user_id=teacher.id, content=com_to_be_cloned.content)
    else:
        # replace the teacher's com content
        teacher_com.content = com_to_be_cloned.content
        # remove the old teacher's notes
        #for note in teacher_com.notes:
        #    # MUST delete commentary_has_note and not the note itself
        #    # (since the latest might be used somewhere else)!
        for chn in CommentaryHasNote.query.filter(CommentaryHasNote.commentary_id == teacher_com.id).all():
            db.session.delete(chn)

        # clone notes
    for chn_to_be_cloned in com_to_be_cloned.commentary_has_note:
        note = Note(type_id=chn_to_be_cloned.note.type_id, user_id=teacher.id,
                    content=chn_to_be_cloned.note.content)
        db.session.add(note)
        db.session.flush()
        teacher_com.transcription_has_note.append(
            CommentaryHasNote(ptr_start=chn_to_be_cloned.ptr_start,
                              ptr_end=chn_to_be_cloned.ptr_end,
                              note_id=note.id,
                              commentary_id=teacher_com.id),
        )

    db.session.add(teacher_com)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200()
