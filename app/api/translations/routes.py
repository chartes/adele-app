from flask import url_for, request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.documents.document_validation import set_document_validation_step
from app.api.routes import api_bp
from app.models import Translation, User, Document, Translation, AlignmentDiscours, \
    Note, TranslationHasNote, VALIDATION_NONE, VALIDATION_TRANSLATION, VALIDATION_TRANSCRIPTION
from app.utils import make_404, make_200, forbid_if_nor_teacher_nor_admin_and_wants_user_data, \
    forbid_if_nor_teacher_nor_admin, make_400, forbid_if_another_teacher, make_403, is_closed, forbid_if_validation_step

"""
===========================
    Translations
===========================
"""


def get_translation(doc_id, user_id):
    return Translation.query.filter(
        doc_id == Translation.doc_id,
        user_id == Translation.user_id
    ).first()


def get_reference_translation(doc_id):
    """

    :param doc_id:
    :return:
    """
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is not None and doc.validation_step >= VALIDATION_TRANSLATION:
        return Translation.query.filter(
            doc_id == Translation.doc_id,
            doc.user_id == Translation.user_id
        ).first()

    return None

@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/users')
def api_documents_translations_users(api_version, doc_id):
    users = []
    try:
        translations = Translation.query.filter(Translation.doc_id == doc_id).all()
        users = User.query.filter(User.id.in_(set([tr.user_id for tr in translations]))).all()
        users = [{"id": user.id, "username": user.username} for user in users]
    except NoResultFound:
        pass
    return make_200(data=users)


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations')
def api_documents_translations(api_version, doc_id):
    tr = get_reference_translation(doc_id)
    if tr is None:
        return make_404()
    return make_200(data=tr.serialize_for_user(tr.user_id))


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id>')
@jwt_required
def api_documents_translations_from_user(api_version, doc_id, user_id=None):
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid
    tr = get_translation(doc_id, user_id)
    if tr is None:
        return make_404()
    return make_200(data=tr.serialize_for_user(user_id))


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id>', methods=["POST"])
@jwt_required
def api_post_documents_translations(api_version, doc_id, user_id):
    """
    at least one of "content" or "notes" is required
    "notes" when there is no tr in base is forbidden so
    you can in a first time post "content" and later "notes", or both at the same time

    NB: Posting notes has a 'TRUNCATE AND REPLACE' effect

    {
        "data":
            {
                "content" :  "My first translation"
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
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    forbid = forbid_if_validation_step(doc_id, gte=VALIDATION_TRANSLATION)
    if forbid:
        return forbid

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    data = request.get_json()
    if "data" in data:
        data = data["data"]
        try:
            # case 1) "content" in data
            if "content" in data:
                tr = Translation(doc_id=doc_id, content=data["content"], user_id=user_id)
            # case 2) there's only "notes" in data
            elif "notes" in data:
                tr = Translation.query.filter(Translation.doc_id == doc_id,
                                                Translation.user_id == user_id).first()
                if tr is None:
                    return make_404()
            else:
                return make_400(details="Wrong data")
            # register new notes if any
            if "notes" in data:
                new_notes = [Note(type_id=n.get("type_id", 0), user_id=user_id, content=n["content"])
                             for n in data["notes"]]
                for n in new_notes:
                    db.session.add(n)
                if len(new_notes) > 0:
                    db.session.flush()
                    # bind new notes to the translation
                    # NB: Posting notes has therefore a 'TRUNCATE AND REPLACE' effect
                    for thn in tr.translation_has_note:
                        if thn.note.user_id == int(user_id):
                            db.session.delete(thn.note)
                    tr.translation_has_note = [TranslationHasNote(translation_id=tr.id,
                                                                      note_id=n.id,
                                                                      ptr_start=data["notes"][num_note]["ptr_start"],
                                                                      ptr_end=data["notes"][num_note]["ptr_end"])
                                                 for num_note, n in enumerate(new_notes)]

            # save the tr and commit all
            db.session.add(tr)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return make_400(str(e))

        return make_200(data=tr.serialize_for_user(user_id))
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id>', methods=["PUT"])
@jwt_required
def api_put_documents_translations(api_version, doc_id, user_id):
    """
     {
         "data":
             {
                 "content" :  "My first translation"  (mandatory)
             }
     }
     :param user_id:
     :param api_version:
     :param doc_id:
     :return:
     """
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    # teachers can still update validated translation
    current_user = current_app.get_current_user()
    if not current_user.is_teacher:
        forbid = forbid_if_validation_step(doc_id, gte=VALIDATION_TRANSLATION)
        if forbid:
            return forbid

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    data = request.get_json()
    if "data" in data:
        data = data["data"]
        tr = get_translation(doc_id=doc_id, user_id=user_id)
        if tr is None:
            return make_404()
        try:
            tr.content = data["content"]
            db.session.add(tr)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_400(str(e))
        return make_200(data=tr.serialize_for_user(user_id))
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id>', methods=["DELETE"])
@jwt_required
def api_delete_documents_translations(api_version, doc_id, user_id):
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    closed = is_closed(doc_id)
    if closed:
        return closed

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_another_teacher = forbid_if_another_teacher(current_app, doc.user_id)
    if is_another_teacher:
        return is_another_teacher

    # forbid students to delete a translation when there is a valid translation
    user = current_app.get_current_user()
    if not user.is_teacher:
        forbid = forbid_if_validation_step(doc_id, gte=VALIDATION_TRANSLATION)
        if forbid:
            return forbid

    tr = get_translation(doc_id=doc_id, user_id=user_id)
    if tr is None:
        return make_404()

    try:
        for thn in tr.translation_has_note:
            if thn.note.user_id == int(user_id):
                db.session.delete(thn.note)
        db.session.delete(tr)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    set_document_validation_step(doc=doc, stage_id=VALIDATION_TRANSCRIPTION)

    return make_200()


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/clone/from-user/<user_id>', methods=['GET'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_clone_translation(api_version, doc_id, user_id):
    print("cloning translation (doc %s) from user %s" % (doc_id, user_id))

    tr_to_be_cloned = Translation.query.filter(Translation.user_id == user_id,
                                                 Translation.doc_id == doc_id).first()

    if not tr_to_be_cloned:
        return make_404()

    teacher = current_app.get_current_user()
    teacher_tr = Translation.query.filter(Translation.user_id == teacher.id,
                                            Translation.doc_id == doc_id).first()
    if teacher_tr is None:
        teacher_tr = Translation(doc_id=doc_id, user_id=teacher.id, content=tr_to_be_cloned.content)
    else:
        # replace the teacher's tr content
        teacher_tr.content = tr_to_be_cloned.content
        # remove the old teacher's notes
        for note in teacher_tr.notes:
            db.session.delete(note)
        # teacher_tr.notes = []

    # clone notes
    for thn_to_be_cloned in tr_to_be_cloned.translation_has_note:
        note = Note(type_id=thn_to_be_cloned.note.type_id, user_id=teacher.id,
                    content=thn_to_be_cloned.note.content)
        db.session.add(note)
        db.session.flush()
        teacher_tr.translation_has_note.append(
            TranslationHasNote(ptr_start=thn_to_be_cloned.ptr_start,
                                 ptr_end=thn_to_be_cloned.ptr_end,
                                 note_id=note.id,
                                 translation_id=teacher_tr.id),
        )

    db.session.add(teacher_tr)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200()
