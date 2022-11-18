from flask import request, current_app
from flask_jwt_extended import jwt_required
from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound

from app import db
from app.api.routes import api_bp
from app.api.transcriptions.routes import get_reference_transcription, add_notes_refs_to_text
from app.models import Commentary, Document, Note, TranscriptionHasNote, CommentaryHasNote, Transcription, findNoteInDoc, set_notes_from_content
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

    return make_200(data=[{
        "doc_id": com["doc_id"],
        "user_id": com["user_id"],
        "type": com["type"],
        "content": Markup(com['content']) if com['content'] is not None else "",
        "notes": {"{:010d}".format(n["id"]): n["content"] for n in com["notes"]}
    } for com in _coms])


def delete_commentary(doc_id, user_id, type_id):
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


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id>',
              methods=['DELETE'])
@jwt_required
def api_delete_commentary(api_version, doc_id, user_id=None, type_id=None):
    return delete_commentary(doc_id, user_id, type_id)


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>', methods=['POST'])
@jwt_required
def api_post_commentary(api_version, doc_id, user_id):
    """
    {
        "data":
            {
                "type_id": 2,
                "content" : "This is a commentary",
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
            error = check_no_XMLParserError(data["content"])
            if error:
                raise Exception('Commentary content is malformed: %s', str(error))
            c = Commentary(doc_id=doc_id, user_id=user_id, type_id=data["type_id"], content=data["content"])
            set_notes_from_content(c)
            db.session.add(c)
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
            error = check_no_XMLParserError(data["content"])
            if error:
                raise Exception('Commentary content is malformed: %s', str(error))
            c.content = data["content"]
            set_notes_from_content(c)
            db.session.add(c)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print('Error', str(e))
            return make_400(str(e))
        return make_200(data=c.serialize())
    else:
        return make_400("no data")


def clone_commentary(doc_id, user_id, type_id):
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
        # for note in teacher_com.notes:
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
        teacher_com.notes.append(note)

    db.session.add(teacher_com)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200()


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/clone/from-user/<user_id>/and-type/<type_id>',
              methods=['GET'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_clone_commentary(api_version, doc_id, user_id, type_id):
    return clone_commentary(doc_id, user_id, type_id)
