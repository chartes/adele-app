import datetime
import pprint
from math import ceil
from urllib.request import build_opener

from flask_jwt_extended import jwt_required
from sqlalchemy import or_, and_

from app.api.routes import api_bp, json_loads
from app.models import Institution, Editor, Country, District, ActeType, Language, Tradition, Whitelist, \
    ImageUrl, Image, Note, CommentaryType, User, CommentaryHasNote, AlignmentTranslation, TranslationHasNote, \
    TranscriptionHasNote, ImageZone
from app.utils import forbid_if_nor_teacher_nor_admin, make_204, make_409, check_no_XMLParserError, forbid_if_not_admin
from ..alignments.alignment_images import clone_alignment_image
from ..alignments.alignments_discours import clone_speechparts
from ..alignments.alignments_translation import clone_translation_alignments
from ..commentaries.routes import clone_commentary, delete_commentary
from ..transcriptions.routes import clone_transcription, get_reference_transcription, delete_document_transcription
from ..translations.routes import clone_translation, delete_document_translation

"""
===========================
    Document
===========================
"""


@api_bp.route('/api/<api_version>/documents/<doc_id>')
def api_documents(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc:
        return make_200(doc.serialize())
    else:
        return make_404("Document {0} not found".format(doc_id))


@api_bp.route('/api/<api_version>/documents/<doc_id>/status')
@jwt_required
def api_documents_status(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()
    return make_200(data=doc.serialize_status())


@api_bp.route('/api/<api_version>/documents/<doc_id>/publish')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_publish(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed

    try:
        doc.is_published = True
        db.session.commit()
        return make_200(data=doc.serialize_status())
    except Exception as e:
        return make_400(str(e))

@api_bp.route('/api/<api_version>/documents/<doc_id>/unpublish')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_unpublish(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed
    try:
        doc.is_published = False
        db.session.commit()
        return make_200(data=doc.serialize_status())
    except Exception as e:
        return make_400(str(e))


@api_bp.route('/api/<api_version>/documents', methods=['POST'])
def api_get_documents(api_version):
    data = request.get_json()
    if data is None:
        data = {}
    page_size = max(data.get("pageSize", 20), 1)
    page_number = max(data.get("pageNum", 1), 1)

    query = Document.query

    filters = data.get("filters", [])

    countMode = data.get('countOnly', False)
    filters_to_count = filters.get("filtersToCount", None)

    filter_stmts = {
        "centuries": None,
        "creationRange": None,
        "copyCenturies": None,
        "traditions": None,
        "languages": None,
        "acteTypes": None,
        "countries": None,
        "districts": None,
        "institutions": None
    }
    filter_models = {
        "traditions": Tradition,
        "languages": Language,
        "acteTypes": ActeType,
        "countries": Country,
        "districts": District,
        "institutions": Institution
    }

    filter_checks = {
        "traditions": Document.traditions.any,
        "languages": Document.languages.any,
        "acteTypes": Document.acte_types.any,
        "countries": Document.countries.any,
        "districts": Document.districts.any,
        "institutions": Document.institution.has
    }

    # FILTERS
    if "centuries" in filters:
        centuries = []
        for c in filters["centuries"]:
            s = int(c["id"])
            centuries.append(Document.creation.between((s-1) * 100, s * 100))
        if len(centuries) > 0:
            filter_stmts["centuries"] = or_(*centuries)

    # same field on the model but dealing with years and not centuries
    if "creationRange" in filters:
        start, end = filters["creationRange"]
        _ors_dates = [Document.creation.between(int(start), int(end))]
        if filters.get("showDocsWithoutDates", False):
            _ors_dates.append(Document.creation.is_(None))
        filter_stmts["creationRange"] = or_(*_ors_dates)

    if "copyCenturies" in filters:
        centuries = []
        for c in filters["copyCenturies"]:
            centuries.append(Document.copy_cent == int(c["id"]))
        if len(centuries) > 0:
            filter_stmts["copyCenturies"] = or_(*centuries)

    if "languages" in filters:
        asked_codes = [c["code"] for c in filters["languages"]]
        if len(asked_codes) > 0:
            filter_stmts["languages"] = Document.languages.any(Language.code.in_(asked_codes))

    if "traditions" in filters:
        asked_traditions = [c["id"] for c in filters["traditions"]]
        if len(asked_traditions) > 0:
            filter_stmts["traditions"] = Document.traditions.any(Tradition.id.in_(asked_traditions))

    if "acteTypes" in filters:
        asked_acteTypes = [c["id"] for c in filters["acteTypes"]]
        if len(asked_acteTypes) > 0:
            filter_stmts["acteTypes"] = Document.acte_types.any(ActeType.id.in_(asked_acteTypes))

    if "countries" in filters:
        asked_countries = [c["id"] for c in filters["countries"]]
        if len(asked_countries) > 0:
            filter_stmts["countries"] = Document.countries.any(Country.id.in_(asked_countries))

    if "districts" in filters:
        asked_districts = [c["id"] for c in filters["districts"]]
        if len(asked_districts) > 0:
             filter_stmts["districts"] = Document.districts.any(District.id.in_(asked_districts))

    if "institutions" in filters:
        asked_institutions = [c["id"] for c in filters["institutions"]]
        if len(asked_institutions) > 0:
            filter_stmts["institutions"] = Document.institution.has(Institution.id.in_(asked_institutions))

    # SORTS
    sorts = []
    for s in data.get("sorts", []):
        if s.startswith('-'):
            isDesc = True
            s = s[1:]
        else:
            isDesc = False

        field = getattr(Document, s)
        if isDesc:
            field = field.desc()
        sorts.append(field)

    access_restrictions = []
    user = current_app.get_current_user()

    if user.is_anonymous:
        access_restrictions.append(Document.is_published)

    # compute the query count independently for each row for the selected filter
    filterCount = {}
    if filters_to_count:
        for filter_to_count in filters_to_count:
            stmts = [v for k, v in filter_stmts.items() if v is not None and k != filter_to_count]
            model = filter_models[filter_to_count]

            model_id = model.id if filter_to_count != "languages" else model.code
            print(filter_to_count, model_id)

            check = filter_checks[filter_to_count]

            filterCount[filter_to_count] = {}
            print("======= count %s =======" % filter_to_count)
            for obj in model.query.all():
                or_stmts = stmts +[check(model_id.in_([obj.id]))]
                q = query.filter(and_(*or_stmts, *access_restrictions))
                filterCount[filter_to_count][obj.id] = q.count()
            print("--->", filterCount[filter_to_count])

    if not countMode:
        s = [v for k, v in filter_stmts.items() if v is not None]
        query = query.filter(and_(*s, *access_restrictions))
        count = query.count()
        if len(sorts) > 0:
            query = query.order_by(*sorts)
        docs = query.paginate(int(page_number), int(page_size), max_per_page=100, error_out=False).items

        meta = {"totalCount": count, "currentPage": page_number, "nbPages": ceil(count / page_size)}
    else:
        meta = {"filterCount": filterCount}
        docs = []

    return make_200(data={"meta": meta,
                          "data": [
                              doc.serialize(zones=False, whitelist=False) for doc in docs
                          ]})


@api_bp.route('/api/<api_version>/documents/bookmarks')
def api_get_documents_get_bookmarks(api_version):
    """
    :param api_version:
    :param doc_id:
    :return:
    """
    user = current_app.get_current_user()

    access_restrictions = [Document.is_published] if user.is_anonymous else []
    docs = Document.query.filter(*access_restrictions, Document.bookmark_order).order_by(Document.bookmark_order).all()

    return make_200(data=[d.serialize() for d in docs])


@api_bp.route('/api/<api_version>/dashboard/bookmarks/<doc_id>/toggle', methods=['GET'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_dashboard_bookmark_document(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    row = db.session.query(func.max(Document.bookmark_order).label('last_id')).first()

    print('update bookmark:', doc_id, doc.bookmark_order)
    if doc.bookmark_order is None:
        doc.bookmark_order = 1 if row.last_id is None else row.last_id + 1
    else:
        doc.bookmark_order = None
    # db.session.add(doc)
    db.session.commit()

    print('--->', doc_id, doc.bookmark_order)

    return make_200(data={'new_order': doc.bookmark_order})


@api_bp.route('/api/<api_version>/dashboard/bookmarks/reorder', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_dashboard_reorder_bookmark_document(api_version):
    data = request.get_json()

    for doc in data['bookmarks']:
        old = Document.query.filter(Document.bookmark_order == doc['bookmark_order']).first()
        old.bookmark_order = None

    db.session.commit()

    for doc in data['bookmarks']:
        new = Document.query.filter(Document.id == doc['docId']).first()
        new.bookmark_order = doc['bookmark_order']

    db.session.commit()

    return make_200()


@api_bp.route('/api/<api_version>/documents', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_documents(api_version):
    data = request.get_json()
    if "data" in data:
        data = data["data"]

    tmp_doc = {
        "title": "Sans titre"
    }
    for key in ("title", "subtitle", "argument", "attribution", "pressmark",
                "creation", "creation_lab", "copy_year", "copy_cent"):
        if key in data:
            tmp_doc[key] = data[key]

    if "institution_id" in data:
        tmp_doc["institution"] = Institution.query.filter(Institution.id == data["institution_id"]).first()

    if "editor_id" in data:
        if not isinstance(data["editor_id"], list):
            data["editor_id"] = [data["editor_id"]]
        tmp_doc["editors"] = Editor.query.filter(Editor.id.in_(data["editor_id"])).all()

    if "country_id" in data:
        if not isinstance(data["country_id"], list):
            data["country_id"] = [data["country_id"]]
        tmp_doc["countries"] = Country.query.filter(Country.id.in_(data["country_id"])).all()

    if "district_id" in data:
        if not isinstance(data["district_id"], list):
            data["district_id"] = [data["district_id"]]
        tmp_doc["districts"] = District.query.filter(District.id.in_(data["district_id"])).all()

    if "acte_type_id" in data:
        if not isinstance(data["acte_type_id"], list):
            data["acte_type_id"] = [data["acte_type_id"]]
        tmp_doc["acte_types"] = ActeType.query.filter(ActeType.id.in_(data["acte_type_id"])).all()

    if "language_code" in data:
        if not isinstance(data["language_code"], list):
            data["language_code"] = [data["language_code"]]
        tmp_doc["languages"] = Language.query.filter(Language.code.in_(data["language_code"])).all()

    if "tradition_id" in data:
        if not isinstance(data["tradition_id"], list):
            data["tradition_id"] = [data["tradition_id"]]
        tmp_doc["traditions"] = Tradition.query.filter(Tradition.id.in_(data["tradition_id"])).all()

    if "linked_document_id" in data:
        if not isinstance(data["linked_document_id"], list):
            data["linked_document_id"] = [data["linked_document_id"]]
        tmp_doc["linked_documents"] = Document.query.filter(Document.id.in_(data["linked_document_id"])).all()

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tmp_doc["date_insert"] = now
    tmp_doc["date_update"] = now

    user = current_app.get_current_user()
    tmp_doc["user_id"] = user.id
    doc = Document(**tmp_doc)

    try:
        db.session.add(doc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))

    return make_200(data=doc.serialize())


@api_bp.route('/api/<api_version>/documents/<doc_id>', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_documents(api_version, doc_id):
    data = request.get_json()
    if "data" in data:
        data = data["data"]

    tmp_doc = Document.query.filter(Document.id == doc_id).first()
    if tmp_doc is None:
        return make_404("Document not found")

    is_not_allowed = forbid_if_not_in_whitelist(current_app, tmp_doc)
    if is_not_allowed:
        return is_not_allowed

    if "title" in data: tmp_doc.title = data["title"]
    if "subtitle" in data: tmp_doc.subtitle = data["subtitle"]
    if "attribution" in data: tmp_doc.attribution = data["attribution"]

    if "argument" in data:
        error = check_no_XMLParserError(data["argument"])
        if error:
            return error
        tmp_doc.argument = data["argument"]

    if "pressmark" in data: tmp_doc.pressmark = data["pressmark"]
    if "creation" in data: tmp_doc.creation = data["creation"]
    if "creation_lab" in data: tmp_doc.creation_lab = data["creation_lab"]
    if "copy_year" in data: tmp_doc.copy_year = data["copy_year"]
    if "copy_cent" in data: tmp_doc.copy_cent = data["copy_cent"]

    if "institution_id" in data:
        tmp_doc.institution = Institution.query.filter(Institution.id == data["institution_id"]).first()

    if "editor_ref" in data:
        tmp_doc.editors = Editor.query.filter(Editor.ref.in_(data["editor_ref"])).all()

    if "country_ref" in data:
        tmp_doc.countries = Country.query.filter(Country.ref.in_(data["country_ref"])).all()

    if "district_id" in data:
        tmp_doc.districts = District.query.filter(District.id.in_(data["district_id"])).all()

    if "acte_type_id" in data:
        tmp_doc.acte_types = ActeType.query.filter(ActeType.id.in_(data["acte_type_id"])).all()

    if "language_code" in data:
        tmp_doc.languages = Language.query.filter(Language.code.in_(data["language_code"])).all()

    if "tradition_id" in data:
        tmp_doc.traditions = Tradition.query.filter(Tradition.id.in_(data["tradition_id"])).all()

    if "linked_document_id" in data:
        tmp_doc.linked_documents = Document.query.filter(Document.id.in_(data["linked_document_id"])).all()

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tmp_doc.date_update = now

    try:
        db.session.add(tmp_doc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))

    return make_200(data=tmp_doc.serialize())


@api_bp.route('/api/<api_version>/documents/<doc_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_documents(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404("Document not found")

    try:
        db.session.delete(doc)
        db.session.commit()
        print("document", doc_id, "deleted")
    except Exception as e:
        db.session.rollback()
        return make_400("Cannot delete data: %s" % str(e))

    return make_204()

@api_bp.route('/api/<api_version>/documents/notes/<note_id>', methods=["DELETE"])
@jwt_required
def api_delete_notes(api_version, note_id):
    current_user = current_app.get_current_user()
    note = Note.query.filter(Note.id == note_id).first()
    if note is None:
        return make_400('This note does not exist')
    if current_user.is_admin or current_user.is_teacher or note.user_id == current_user.id:
        try:
            db.session.delete(note)
            db.session.commit()
            return make_200()
        except Exception as e:
            db.session.rollback()
            return make_400("Cannot delete data: %s" % str(e))
    else:
        return make_403('You cannot delete this note')

@api_bp.route('/api/<api_version>/documents/<doc_id>/whitelist', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_change_documents_whitelist(api_version, doc_id):
    """
    {
        "data" : {
            "whitelist_id" : 1
        }
    }
    :param api_version:
    :param doc_id:
    :return:
    """

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    data = request.get_json()
    data = data.get('data')

    try:
        new_white_list_id = data.get('whitelist_id')
        if new_white_list_id is None:
            doc.whitelist_id = None
        else:
            wl = Whitelist.query.filter(Whitelist.id == new_white_list_id).first()
            doc.whitelist = wl
        db.session.commit()
    except Exception as e:
        return make_400(str(e))

    return make_200()


@api_bp.route('/api/<api_version>/documents/<doc_id>/open')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_change_documents_open(api_version, doc_id):
    """
    :param api_version:
    :param doc_id:
    :return:
    """
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    doc.date_closing = None
    db.session.add(doc)
    db.session.commit()

    return make_200(data=doc.serialize_status())


@api_bp.route('/api/<api_version>/documents/<doc_id>/close', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_change_documents_closing_date(api_version, doc_id):
    """
    {
        "data" : {
            "closing_date" : "15/10/2020"
        }
    }
    # dd/mm/YYYY
    :param api_version:
    :param doc_id:
    :return:
    """

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    data = request.get_json()
    data = data.get('data')
    try:
        new_closing_date = data.get('closing_date')
        if not new_closing_date or len(new_closing_date) == 0:
            new_closing_date = None
        else:
            new_closing_date = datetime.datetime.strptime(new_closing_date, '%d/%m/%Y')
            new_closing_date = new_closing_date.strftime('%Y-%m-%d %H:%M:%S')

        doc.date_closing = new_closing_date
        db.session.commit()
    except Exception as e:
        return make_400(str(e))

    return make_200(data=doc.serialize_status())


@api_bp.route('/api/<api_version>/documents/add', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_add_document(api_version):

    data = request.get_json()
    data = data["data"]

    user = current_app.get_current_user()
    kwargs = {
        "title": data.get('title'),
        "subtitle": data.get('subtitle'),
        "user_id": user.id,
        "is_published": 1,
        "whitelist_id": data.get('whitelist-id', 34)  # TODO
    }

    new_doc = Document(**kwargs)
    db.session.add(new_doc)
    db.session.commit()
    return make_200(data=new_doc.serialize())


@api_bp.route('/api/<api_version>/documents/<doc_id>/iiif/manifest', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_document_manifest(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed

    data = request.get_json()
    data = data["data"]
    manifest_url = data.get("manifest_url")

    if Image.query.filter(Image.manifest_url == manifest_url).first() or \
            ImageUrl.query.filter(ImageUrl.manifest_url == manifest_url).first():
        return make_409(
            details="This manifest is already used by another document. Please choose another or upload it to another "
                    "URL. "
        )

    # FETCH the manifest
    try:
        op = build_opener()
        manifest = op.open(manifest_url, timeout=20).read()
        manifest = json_loads(manifest)
    except Exception as e:
        return make_400(details="Cannot fetch manifest: %s" % str(e))

    # delete old images
    for old_image in Image.query.filter(Image.doc_id == doc.id).all():
        db.session.delete(old_image)
    for old_image_url in ImageUrl.query.filter(ImageUrl.manifest_url == manifest_url).all():
        db.session.delete(old_image_url)

    # add new images
    for canvas_idx, canvas in enumerate(manifest["sequences"][0]['canvases']):
        for img_idx, img in enumerate(canvas["images"]):
            new_img = Image(manifest_url=manifest_url, canvas_idx=canvas_idx, img_idx=img_idx, doc_id=doc_id)
            new_img_url = ImageUrl(manifest_url=manifest_url, canvas_idx=canvas_idx, img_idx=img_idx,
                                   img_url=img["resource"]["@id"])
            db.session.add(new_img)
            db.session.add(new_img_url)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_400(details=str(e))

    return make_200(data=[i.serialize() for i in doc.images])


@api_bp.route('/api/<api_version>/documents/<doc_id>/transfer-ownership/<user_id>', methods=['GET'])
@jwt_required
@forbid_if_not_admin
def api_transfer_document_ownership(api_version, doc_id, user_id):
    doc = Document.query.filter(Document.id == doc_id).first()

    validation_flags = doc.validation_flags

    current_owner = User.query.filter(User.id == doc.user_id).first()
    new_owner = User.query.filter(User.id == user_id).first()
    transfered_items = {}

    if new_owner.id == current_owner.id:
        print("[ownership transfer] same user")
        return make_200(data=transfered_items)

    if new_owner.is_teacher:
        print("[ownership transfer] the new user is a teacher")
        # 0) check the current owner has some content to transfer...
        tr = Transcription.query.filter(Transcription.doc_id == doc_id, Transcription.user_id == current_owner.id).first()
        if tr:
            # 1) delete the current content of the new_owner
            current_coms = Commentary.query.filter(Commentary.doc_id == doc_id, Commentary.user_id == new_owner.id).all()
            for pcom in current_coms:
                resp = delete_commentary(doc_id, new_owner.id, pcom.type_id)
                print('delete commentary...', resp.status_code)

            resp = delete_document_translation(doc_id, new_owner.id)
            print('delete translation...', resp.status_code)

            resp = delete_document_transcription(doc_id, new_owner.id)
            print('delete transcription...', resp.status_code)

            # 2) transfer the ownership from the current_owner to the new_owner
            doc.user_id = new_owner.id
            transfered_items['document'] = doc.id
            db.session.commit()

            print('current owner:', current_owner, " new owner:", new_owner)

            # 3) transfer the content from the current_owner to the new_owner

            # transcription
            tr.user_id = new_owner.id
            transfered_items['transcription'] = {tr.id: []}
            # transcription notes
            notes = [thn.note for thn in
                     TranscriptionHasNote.query.filter(TranscriptionHasNote.transcription_id == tr.id).all()]
            for note in notes:
                note.user_id = new_owner.id
                transfered_items['transcription'][tr.id].append(note.id)

            # translation
            tl = Translation.query.filter(Translation.doc_id == doc_id,
                                          Translation.user_id == current_owner.id).first()
            if tl:
                tl.user_id = new_owner.id
                transfered_items['translation'] = {tl.id: []}

                # translation notes
                notes = [thn.note for thn in
                         TranslationHasNote.query.filter(TranslationHasNote.translation_id == tl.id).all()]
                for note in notes:
                    note.user_id = new_owner.id
                    transfered_items['translation'][tl.id].append(note.id)

            # translation alignments not needed becaues the tr and tl ids dont change

            # commentaries
            transfered_items['commentaries'] = {}
            for com in Commentary.query.filter(Commentary.doc_id == doc_id,
                                               Commentary.user_id == current_owner.id).all():
                com.user_id = new_owner.id
                transfered_items['commentaries'][com.id] = []

                # commentary notes
                notes = [chn.note for chn in CommentaryHasNote.query.filter(CommentaryHasNote.commentary_id == com.id).all()]
                for note in notes:
                    note.user_id = new_owner.id
                    transfered_items['commentaries'][com.id].append(note.id)

            # speech parts
            transfered_items['speechparts'] = []
            for al in AlignmentDiscours.query.filter(AlignmentDiscours.transcription_id == tr.id,
                                                      AlignmentDiscours.user_id == current_owner.id).all():
                al.user_id = new_owner.id
                transfered_items['speechparts'].append(al.id)

            # image alignments
            for al in AlignmentImage.query.filter(AlignmentImage.transcription_id == tr.id,
                                                   AlignmentImage.user_id == current_owner.id).all():

                # image zone
                zone = ImageZone.query.filter(ImageZone.zone_id == al.zone_id,
                                       ImageZone.manifest_url == al.manifest_url,
                                       ImageZone.canvas_idx == al.canvas_idx,
                                       ImageZone.img_idx == al.img_idx,
                                       ImageZone.user_id == current_owner.id).first()

                new_zone = ImageZone(
                    zone_id=zone.zone_id,
                    manifest_url=zone.manifest_url,
                    canvas_idx=zone.canvas_idx,
                    img_idx=zone.img_idx,
                    user_id=new_owner.id,
                    zone_type_id=zone.zone_type_id,
                    fragment=zone.fragment,
                    svg=zone.svg,
                    note=zone.note
                )
                new_al = AlignmentImage(
                    transcription_id=al.transcription_id,
                    user_id=new_owner.id,
                    zone_id=al.zone_id,
                    manifest_url=al.manifest_url,
                    canvas_idx=al.canvas_idx,
                    img_idx=al.img_idx,
                    ptr_transcription_start=al.ptr_transcription_start,
                    ptr_transcription_end=al.ptr_transcription_end
                )

                db.session.delete(zone)
                db.session.commit()

                db.session.add(new_zone)
                db.session.commit()
                db.session.add(new_al)

                transfered_items['image-als'] = new_al.zone_id

            # restore validation flags
            doc.is_notice_validated = validation_flags['notice']
            doc.is_transcription_validated = validation_flags['transcription']
            doc.is_translation_validated = validation_flags['translation']
            doc.is_facsimile_validated = validation_flags['facsimile']
            doc.is_speechparts_validated = validation_flags['speech-parts']
            doc.is_commentaries_validated = validation_flags['commentaries']

            db.session.commit()
        else:
            # 1) transfer the ownership from the current_owner to the new_owner
            doc.user_id = new_owner.id
            transfered_items['document'] = doc.id
            db.session.commit()

        print('transfered items:')
        pprint.pprint(transfered_items)
        return make_200(data=transfered_items)
    else:
        return make_403(details="User must be a teacher")


@api_bp.route('/api/<api_version>/document/<doc_id>/clone-contents', methods=['GET'])
@jwt_required
@forbid_if_not_admin
def api_document_clone_contents(api_version, doc_id):
    user = current_app.get_current_user()

    doc = Document.query.filter(Document.id == doc_id).first()
    old_user_id = doc.user_id

    resp = clone_transcription(doc_id, user.id)
    print("clone transcription status:", resp.status)

    if resp.status == 200:

        resp = clone_translation(doc_id, user.id)
        print("clone translation status:", resp.status)

        for com_typ in CommentaryType.query.all():
            resp = clone_commentary(doc_id, user.id, com_typ.id)
            print("clone commentary status:", com_typ.id, resp.status)

        resp = clone_speechparts(doc_id, old_user_id, user.id)
        print("clone speechparts status:", resp.status)

        resp = clone_alignment_image(doc_id, old_user_id, user.id)
        print("clone image alignments status:", resp.status)

        resp = clone_translation_alignments(doc_id, old_user_id, user.id)
        print("clone translation alignments status:", resp.status)


# IMPORT DOCUMENT VALIDATION STEP ROUTES
from .document_validation import *
from .document_management import *
