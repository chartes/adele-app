import datetime

from bs4 import BeautifulSoup
from flask import current_app, url_for
from sqlalchemy import ForeignKeyConstraint, desc
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import case

from app import db

association_document_has_acte_type = db.Table('document_has_acte_type',
                                              db.Column('doc_id', db.Integer, db.ForeignKey('document.id'),
                                                        primary_key=True),
                                              db.Column('type_id', db.Text, db.ForeignKey('acte_type.id'),
                                                        primary_key=True)
                                              )
association_document_has_editor = db.Table('document_has_editor',
                                           db.Column('doc_id', db.Integer, db.ForeignKey('document.id'),
                                                     primary_key=True),
                                           db.Column('editor_id', db.Integer, db.ForeignKey('editor.id'),
                                                     primary_key=True)
                                           )
association_document_has_language = db.Table('document_has_language',
                                             db.Column('doc_id', db.Integer, db.ForeignKey('document.id'),
                                                       primary_key=True),
                                             db.Column('lang_code', db.String, db.ForeignKey('language.code'),
                                                       primary_key=True)
                                             )
association_document_has_tradition = db.Table('document_has_tradition',
                                              db.Column('doc_id', db.Integer, db.ForeignKey('document.id'),
                                                        primary_key=True),
                                              db.Column('tradition_id', db.String, db.ForeignKey('tradition.id'),
                                                        primary_key=True)
                                              )
association_document_from_country = db.Table('document_from_country',
                                             db.Column('doc_id', db.Integer, db.ForeignKey('document.id'),
                                                       primary_key=True),
                                             db.Column('country_id', db.Integer, db.ForeignKey('country.id'),
                                                       primary_key=True)
                                             )
association_document_from_district = db.Table('document_from_district',
                                              db.Column('doc_id', db.Integer, db.ForeignKey('document.id'),
                                                        primary_key=True),
                                              db.Column('district_id', db.Integer, db.ForeignKey('district.id'),
                                                        primary_key=True)
                                              )
association_user_has_role = db.Table('user_has_role',
                                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                                     db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
                                     )
association_document_linked_to_document = db.Table('document_linked_to_document',
                                                   db.Column('doc_id', db.Integer, db.ForeignKey('document.id'),
                                                             primary_key=True),
                                                   db.Column('linked_doc_id', db.Integer, db.ForeignKey('document.id'),
                                                             primary_key=True),
                                                   )
association_whitelist_has_user = db.Table('whitelist_has_user',
                                          db.Column('whitelist_id', db.Integer, db.ForeignKey('whitelist.id'),
                                                    primary_key=True),
                                          db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                                          )

"""
=======================
    Validation 
=======================

Un flag de validation distinct pour chaque élément du dossier parmi la liste suivante :
- transcription
- traduction
- commentaires
- alignements transcription / facsimile
- alignements transcription / parties du discours

Les flags sont des booléens (0: non validé, 1: validé)

Les flags suivants ne peuvent être validés que si le flag transcription est validé :
- traduction
- commentaires
- alignements transcription / facsimile
- alignements transcription / parties du discours

Invalider le flag transcription invalide automatiquement les flags suivants :
- traduction
- commentaires
- alignements transcription / facsimile
- alignements transcription / parties du discours

"""

TR_ZONE_TYPE = 1  # transcriptions
ANNO_ZONE_TYPE = 2  # annotations


class ActeType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String)
    description = db.Column(db.String)

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'description': self.description
        }


class AlignmentImage(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, primary_key=True)
    manifest_url = db.Column(db.String, primary_key=True)
    canvas_idx = db.Column(db.Integer, primary_key=True)
    img_idx = db.Column(db.Integer, primary_key=True)

    ptr_transcription_start = db.Column(db.Integer)
    ptr_transcription_end = db.Column(db.Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ("user_id", "zone_id", "manifest_url", "canvas_idx", "img_idx"),
            ["image_zone.user_id", "image_zone.zone_id", "image_zone.manifest_url", "image_zone.canvas_idx",
             "image_zone.img_idx"],
            name="fk_alignment_image",
            ondelete='CASCADE'
        ),
    )

    def serialize(self):
        return {
            'transcription_id': self.transcription_id,
            'manifest_url': self.manifest_url,
            'user_id': self.user_id,
            'canvas_idx': self.canvas_idx,
            'img_idx': self.canvas_idx,
            'zone_id': self.zone_id,
            'ptr_start': self.ptr_transcription_start,
            'ptr_end': self.ptr_transcription_end
        }


class AlignmentTranslation(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id', ondelete='CASCADE'), primary_key=True)
    translation_id = db.Column(db.Integer, db.ForeignKey('translation.id', ondelete='CASCADE'), primary_key=True)
    ptr_transcription_start = db.Column(db.Integer, primary_key=True)
    ptr_transcription_end = db.Column(db.Integer, primary_key=True)
    ptr_translation_start = db.Column(db.Integer, primary_key=True)
    ptr_translation_end = db.Column(db.Integer, primary_key=True)

    transcription = db.relationship("Transcription")
    translation = db.relationship("Translation")

    def serialize(self):
        return {
            'transcription_id': self.transcription_id,
            'translation_id': self.translation_id,
            'ptr_transcription_start': self.ptr_transcription_start,
            'ptr_transcription_end': self.ptr_transcription_end,
            'ptr_translation_start': self.ptr_translation_start,
            'ptr_translation_end': self.ptr_translation_end
        }


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ref = db.Column(db.String)
    label = db.Column(db.String)

    districts = db.relationship("District", cascade="all, delete-orphan", passive_deletes=True)

    def serialize(self):
        return {
            'id': self.id,
            'ref': self.ref,
            'label': self.label,
            "districts": [d.serialize() for d in self.districts]
        }


class CommentaryType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String)

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label
        }


class Commentary(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'))
    type_id = db.Column(db.Integer, db.ForeignKey('commentary_type.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.Text)

    type = db.relationship("CommentaryType", backref="commentary")
    notes = db.relationship('Note', secondary='commentary_has_note', back_populates='commentaries', collection_class=set)

    __table_args__ = (
        db.UniqueConstraint('doc_id', 'user_id', 'type_id', name='UniqueCommentaryType'),
    )

    def notes_of_user(self, user_id):
        return [
            note.serialize()
            for note in self.notes if note.user_id == int(user_id)]

    def serialize(self):
        return {
            'doc_id': self.doc_id,
            'user_id': self.user_id,
            'type': self.type.serialize(),
            'content': self.content,
            'notes': self.notes_of_user(self.user_id)
        }


class CommentaryHasNote(db.Model):
    commentary_id = db.Column(db.Integer, db.ForeignKey('commentary.id', ondelete='CASCADE'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), primary_key=True)
    ptr_start = db.Column(db.Integer, primary_key=True)
    ptr_end = db.Column(db.Integer, primary_key=True)


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id', ondelete='CASCADE'))

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'country_id': self.country_id,
        }


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(), nullable=False, unique=False)
    subtitle = db.Column(db.String(), nullable=False, unique=False)
    creation = db.Column(db.String)
    creation_lab = db.Column(db.String())
    copy_year = db.Column(db.String())
    copy_cent = db.Column(db.Integer)
    pressmark = db.Column(db.String())
    argument = db.Column(db.Text())
    attribution = db.Column(db.Text())
    bookmark_order = db.Column(db.Integer, unique=True)
    date_insert = db.Column(db.String())
    date_update = db.Column(db.String())
    date_closing = db.Column(db.String())
    is_published = db.Column(db.Boolean())
    institution_id = db.Column(db.Integer(), db.ForeignKey("institution.id"))
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id", ondelete='CASCADE'))
    whitelist_id = db.Column(db.Integer(), db.ForeignKey("whitelist.id"))

    # validation flags
    is_notice_validated = db.Column(db.Boolean(), default=True)
    is_transcription_validated = db.Column(db.Boolean(), default=False)
    is_translation_validated = db.Column(db.Boolean(), default=False)
    is_facsimile_validated = db.Column(db.Boolean(), default=False)
    is_speechparts_validated = db.Column(db.Boolean(), default=False)
    is_commentaries_validated = db.Column(db.Boolean(), default=False)

    # Relationships #
    whitelist = db.relationship("Whitelist", primaryjoin="Document.whitelist_id==Whitelist.id",
                                backref=db.backref('documents'))
    user = db.relationship("User", primaryjoin="Document.user_id==User.id", backref=db.backref('documents'))

    images = db.relationship("Image", primaryjoin="Document.id==Image.doc_id",
                             backref=db.backref('document'),
                             cascade="all, delete-orphan", single_parent=True, passive_deletes=True
                             )

    institution = db.relationship("Institution", primaryjoin="Document.institution_id==Institution.id",
                                  backref=db.backref('documents'))
    acte_types = db.relationship(ActeType,
                                 secondary=association_document_has_acte_type,
                                 backref=db.backref('documents', ))
    countries = db.relationship("Country",
                                secondary=association_document_from_country,
                                backref=db.backref('documents', ))
    districts = db.relationship("District",
                                secondary=association_document_from_district,
                                backref=db.backref('documents', ))
    editors = db.relationship("Editor",
                              secondary=association_document_has_editor,
                              backref=db.backref('documents', ))
    languages = db.relationship("Language",
                                secondary=association_document_has_language,
                                backref=db.backref('documents'))
    traditions = db.relationship("Tradition",
                                 secondary=association_document_has_tradition,
                                 backref=db.backref('documents'))
    linked_documents = db.relationship("Document",
                                       secondary=association_document_linked_to_document,
                                       primaryjoin=(association_document_linked_to_document.c.doc_id == id),
                                       secondaryjoin=(association_document_linked_to_document.c.linked_doc_id == id))

    validated_commentaries = db.relationship("Commentary",
                          primaryjoin="and_(Commentary.user_id == Document.user_id,Commentary.doc_id == Document.id, Document.is_commentaries_validated == True)")

    @hybrid_property
    def witness_date(self):
        d = self.copy_cent if (self.copy_cent - 1) * 100  else self.creation
        print(d)
        return d
    @witness_date.expression
    def witness_date(cls):
        return case([
            (cls.copy_cent != None, (cls.copy_cent - 1) * 100),
        ], else_=cls.creation)

    @property
    def is_closed(self):
        if not self.date_closing:
            return False
        else:
            #user = current_app.get_current_user()
            #if (user.is_teacher) or user.is_admin:
            #    return False
            doc_closing_time = datetime.datetime.strptime(self.date_closing, '%Y-%m-%d %H:%M:%S')
            return datetime.datetime.now() > doc_closing_time

    @property
    def manifest_url(self):
        return current_app.with_url_prefix(url_for('api_bp.api_documents_manifest', api_version='1.0', doc_id=self.id))

    @property
    def validation_flags(self):
        tr = Transcription.query.filter(Transcription.doc_id == self.id,
                                           Transcription.user_id == self.user_id).first()

        tl = Translation.query.filter(Translation.doc_id == self.id,
                                      Translation.user_id == self.user_id).first()

        alignment_translation_validated = False
        if tr is not None and tl is not None:
            tr_alignments_count = len(BeautifulSoup(tr.content, 'html.parser').find_all('adele-segment'))
            tl_alignments_count = len(BeautifulSoup(tl.content, 'html.parser').find_all('adele-segment'))
            alignment_translation_validated = tr_alignments_count == tl_alignments_count
        return {
            'notice': self.is_notice_validated is True,
            'transcription': self.is_transcription_validated is True,
            'translation': self.is_translation_validated is True,
            'alignment-translation': alignment_translation_validated,
            'facsimile': self.is_facsimile_validated is True,
            'speech-parts': self.is_speechparts_validated is True,
            'commentaries': self.is_commentaries_validated is True
        }

    @property
    def exist_flags(self):
        # owner has content

        tr = Transcription.query.filter(Transcription.doc_id == self.id,
                                           Transcription.user_id == self.user_id).first()

        tl = Translation.query.filter(Translation.doc_id == self.id,
                                      Translation.user_id == self.user_id).first()

        alignment_translation_exists = False
        if tr is not None and tl is not None:
            has_tr_alignment = len(BeautifulSoup(tr.content, 'html.parser').find_all('adele-segment')) > 0
            has_tl_alignment = len(BeautifulSoup(tl.content, 'html.parser').find_all('adele-segment')) > 0
            alignment_translation_exists = has_tr_alignment and has_tl_alignment

        return {
            'notice': True,
            'transcription': tr is not None,
            'translation': tl is not None,
            'alignment-translation': alignment_translation_exists,
            'facsimile': tr is not None and AlignmentImage.query.filter(AlignmentImage.transcription_id == tr.id,
                                                                        AlignmentImage.user_id == self.user_id).count() > 0,
            'speech-parts': tr is not None and SpeechParts.query.filter(SpeechParts.doc_id == self.id,
                                                                              SpeechParts.user_id == self.user_id).count() > 0,
            'commentaries': Commentary.query.filter(Commentary.doc_id == self.id,
                                                    Commentary.user_id == self.user_id).count() > 0,
        }

    def serialize(self, zones=True, whitelist=True):

        prev = db.session.query(Document.id).filter(Document.id < self.id).order_by(desc(Document.id)).first()
        prev_doc_id = prev[0] if prev else None
        next = db.session.query(Document.id).filter(Document.id > self.id).order_by(Document.id).first()
        next_doc_id = next[0] if next else None

        data = {
            'prev_doc_id': prev_doc_id,
            'next_doc_id': next_doc_id,

            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.serialize(),
            'title': self.title,
            'subtitle': self.subtitle,
            'creation': self.creation,
            'creation_lab': self.creation_lab,
            'copy_year': self.copy_year,
            'copy_cent': self.copy_cent,
            'pressmark': self.pressmark,
            'argument': self.argument,
            'attribution': self.attribution,
            'bookmark_order': self.bookmark_order,
            'date_insert': self.date_insert,
            'date_update': self.date_update,
            'date_closing': self.date_closing,
            'images': [im.serialize(zones) for im in self.images],
            'is_published': self.is_published,
            'is_closed': self.is_closed,
            'institution_id': self.institution.id if self.institution is not None else None,
            'institution': self.institution.serialize() if self.institution is not None else None,
            'manifest_url': self.manifest_url,
            'manifest_origin_url': self.images[0].manifest_url if len(self.images) > 0 else None,
            'acte_types': [at.serialize() for at in self.acte_types],
            'countries': [co.serialize() for co in self.countries],
            'districts': [di.serialize() for di in self.districts],
            'editors': [ed.serialize() for ed in self.editors],
            'languages': [lg.serialize() for lg in self.languages],
            'traditions': [tr.serialize() for tr in self.traditions],
            'validation_flags': self.validation_flags,
            'exist_flags': self.exist_flags,
        }

        if whitelist:
            data['whitelist'] = self.whitelist.serialize() if self.whitelist is not None else None

        return data

    def serialize_status(self):
        return {
            'validation-flags': self.validation_flags,
            'exist-flags': self.exist_flags,
            'is-published': self.is_published,
            'is-closed': self.is_closed,
            'date-closing': self.date_closing
        }

    @property
    def validated_commentaries_types(self):
        t = []
        for c in self.validated_commentaries:
            if c.type:
                t.append(c.type)
        return t


class Editor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ref = db.Column(db.String)
    name = db.Column(db.String)

    def serialize(self):
        return {
            'id': self.id,
            'ref': self.ref,
            'name': self.name
        }


class ImageZoneType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String)

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label
        }


class ImageZone(db.Model):
    zone_id = db.Column(db.Integer, primary_key=True)
    manifest_url = db.Column(db.String, primary_key=True)
    canvas_idx = db.Column(db.Integer, primary_key=True)
    img_idx = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    zone_type_id = db.Column(db.Integer, db.ForeignKey('image_zone_type.id', ondelete='CASCADE'))
    fragment = db.Column(db.String)
    svg = db.Column(db.String)
    note = db.Column(db.String)

    __table_args__ = (
        ForeignKeyConstraint(
            ("manifest_url", "canvas_idx", "img_idx"),
            ["image.manifest_url", "image.canvas_idx", "image.img_idx"],
            name="fk_image",
            ondelete='CASCADE'
        ),
    )

    zone_type = db.relationship("ImageZoneType", primaryjoin="ImageZoneType.id==ImageZone.zone_type_id",
                                backref=db.backref('image_zones'))

    def serialize(self):
        return {
            'manifest_url': self.manifest_url,
            'canvas_idx': self.canvas_idx,
            'img_idx': self.img_idx,
            'zone_id': self.zone_id,
            'user_id': self.user_id,
            'zone_type': self.zone_type.serialize(),
            'fragment': self.fragment,
            'svg': self.svg,
            'note': self.note
        }


class ImageUrl(db.Model):
    manifest_url = db.Column(db.String, primary_key=True)
    canvas_idx = db.Column(db.Integer, primary_key=True)
    img_idx = db.Column(db.Integer, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ("manifest_url", "canvas_idx", "img_idx"),
            ["image.manifest_url", "image.canvas_idx", "image.img_idx"],
            name="fk_image",
            ondelete='CASCADE'
        ),
    )

    img_url = db.Column(db.String)

    def serialize(self):
        return {
            'manifest_url': self.manifest_url,
            'canvas_idx': self.canvas_idx,
            'img_idx': self.img_idx,
            'img_url': self.img_url
        }


class Image(db.Model):
    manifest_url = db.Column(db.String, primary_key=True)
    canvas_idx = db.Column(db.Integer, primary_key=True)
    img_idx = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'))

    zones = db.relationship("ImageZone",
                            primaryjoin="and_(ImageZone.manifest_url == Image.manifest_url, ImageZone.canvas_idx == Image.canvas_idx, ImageZone.img_idx == Image.img_idx)",
                            cascade="all, delete-orphan", passive_deletes=True)
    _image_url = db.relationship("ImageUrl",
                                 primaryjoin="and_(ImageUrl.manifest_url == Image.manifest_url,ImageUrl.canvas_idx == Image.canvas_idx, ImageUrl.img_idx == Image.img_idx)",
                                 uselist=False,
                                 cascade="all, delete-orphan", passive_deletes=True)

    # doc = db.relationship("Document", primaryjoin="Document.id==Image.doc_id",
    #                            backref=db.backref('images'), cascade="all, delete-orphan", single_parent=True, passive_deletes=True)

    @property
    def url(self):
        return self._image_url.img_url

    def serialize(self, zones=True):
        data = {
            'canvas_idx': self.canvas_idx,
            'img_idx': self.img_idx,
            'doc_id': self.doc_id,
            'manifest_url': self.manifest_url,

            'url': self.url,
            'thumbnail_url': self.url.replace("full/full", "full/800,"),
            # first approx; should rather open the manifest and seek the real thumbnail url
            'info': self._image_url.img_url[:self._image_url.img_url.rfind('/full/full/')] + '/info.json'
        }
        if zones:
            data['zones'] = [
                {
                    "zone_id": z.zone_id,
                    "user_id": z.user_id,
                    "fragment": z.fragment,
                    "svg": z.svg,
                    "note": z.note

                } for z in self.zones
            ]
        return data


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ref = db.Column(db.String)
    name = db.Column(db.String)

    def serialize(self):
        return {
            'id': self.id,
            'ref': self.ref,
            'name': self.name
        }


class Language(db.Model):
    code = db.Column(db.String, primary_key=True)
    label = db.Column(db.String)

    @property
    def id(self):
        return self.code

    def serialize(self):
        return {
            'code': self.code,
            'label': self.label
        }


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('note_type.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.Text)

    note_type = db.relationship("NoteType", backref=db.backref('note', passive_deletes=True))

    transcriptions = db.relationship(
        "Transcription",
        secondary='transcription_has_note',
        back_populates="notes",
        collection_class = set,
        cascade="delete"
    )
    translations = db.relationship(
        "Translation", 
        secondary='translation_has_note',
        back_populates="notes",
    )
    commentaries = db.relationship(
        "Commentary",
        secondary='commentary_has_note',
        back_populates="notes",
    )

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'type_id': self.type_id,
        }

    def delete_if_unused(self):
        if TranscriptionHasNote.query.filter(TranscriptionHasNote.note_id == self.id).first() is None:
            print("NOTE IN TranscriptionHasNote", self, self.id)

            if TranslationHasNote.query.filter(TranslationHasNote.note_id == self.id).first() is None:
                print("NOTE IN TranslationHasNote", self, self.id)

                if CommentaryHasNote.query.filter(CommentaryHasNote.note_id == self.id).first() is None:
                    print("YES DELETE", self, self.id)
                    db.session.delete(self)
                    db.session.flush()
                    return True
        return False


class NoteType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String)

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label
        }


# Define the Role DataModel
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(), unique=True)
    description = db.Column(db.String())
    label = db.Column(db.String())

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'label': self.label
        }


class SpeechPartType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lang_code = db.Column(db.String, db.ForeignKey("language.code", ondelete="CASCADE"))
    label = db.Column(db.String)
    definition = db.Column(db.Text)

    language = db.relationship("Language", primaryjoin=(Language.code == lang_code))

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'language': self.language.serialize() if self.language else None,
            'definition': self.definition if self.definition else ''
        }


class Tradition(db.Model):
    id = db.Column(db.String, primary_key=True)
    label = db.Column(db.String)
    definition = db.Column(db.Text)

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'definition': self.definition if self.definition else ''
        }


class TranscriptionHasNote(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id', ondelete='CASCADE'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), primary_key=True)
    ptr_start = db.Column(db.Integer)
    ptr_end = db.Column(db.Integer)


class Transcription(db.Model):
    __table_args__ = (
        db.UniqueConstraint('doc_id', 'user_id', name='uix_user', ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.Text)

    notes = db.relationship('Note', secondary='transcription_has_note', back_populates='transcriptions', collection_class=set, cascade="delete")

    def notes_of_user(self, user_id):
        return [
            note.serialize()
            for note in self.notes
            if note.user_id == int(user_id)
        ]

    def serialize_for_user(self, user_id):
        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'user_id': self.user_id,
            'content': self.content,
            'notes': self.notes_of_user(user_id)
        }


class SpeechParts(db.Model):
    __table_args__ = (
        db.UniqueConstraint('doc_id', 'user_id', name='uix_user', ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.Text)

    def serialize(self):
        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'user_id': self.user_id,
            'content': self.content,
        }


class TranslationHasNote(db.Model):
    translation_id = db.Column(db.Integer, db.ForeignKey('translation.id', ondelete='CASCADE'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), primary_key=True)
    ptr_start = db.Column(db.Integer, primary_key=True)
    ptr_end = db.Column(db.Integer, primary_key=True)


class Translation(db.Model):
    __table_args__ = (
        db.UniqueConstraint('doc_id', 'user_id', name='uix_user'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.Text)

    notes = db.relationship('Note', secondary='translation_has_note', back_populates='translations', collection_class=set)

    def notes_of_user(self, user_id):
        return [
            note.serialize()
            for note in self.notes
            if note.user_id == int(user_id)
        ]

    def serialize_for_user(self, user_id):
        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'user_id': self.user_id,
            'content': self.content,
            'notes': self.notes_of_user(user_id)
        }


def findNoteInDoc(doc_id, user_id, note_id):
    transcription = Transcription.query.filter(Transcription.doc_id == doc_id,
                                               Transcription.user_id == user_id).first()
    if transcription:
        thn = TranscriptionHasNote.query.filter(TranscriptionHasNote.transcription_id == transcription.id,
                                                 TranscriptionHasNote.note_id == note_id).first()
        if thn:
            return thn.note

    translation = Translation.query.filter(Translation.doc_id == doc_id,
                                           Translation.user_id == user_id).first()
    if translation:
        thn = TranslationHasNote.query.filter(TranslationHasNote.translation_id == translation.id,
                                               TranslationHasNote.note_id == note_id).first()
        if thn:
            return thn.note

    coms = Commentary.query.filter(Commentary.doc_id == doc_id,
                                   Commentary.user_id == user_id).all()
    for com in coms:
        chn = CommentaryHasNote.query.filter(CommentaryHasNote.commentary_id == com.id,
                                              CommentaryHasNote.note_id == note_id).first()
        if chn:
            return chn.note

    print("note find", note_id, user_id, Note.query.filter(Note.id == note_id, Note.user_id == user_id).first())
    return Note.query.filter(Note.id == note_id, Note.user_id == user_id).first()


class AnonymousUser(object):
    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return

    @property
    def documents_i_can_edit(self):
        return []

    @property
    def is_teacher(self):
        return False

    @property
    def is_admin(self):
        return False

    @property
    def is_student(self):
        return False


# Define the User data model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User authentication information
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(), nullable=False, unique=True)
    email_confirmed_at = db.Column('confirmed_at', db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column('firstname', db.String(), nullable=False, server_default='')
    last_name = db.Column('lastname', db.String(), nullable=False, server_default='')

    # Relationships
    roles = db.relationship('Role', secondary=association_user_has_role,
                            backref=db.backref('users', lazy='dynamic'))

    # def __init__(self, *args, **kwargs):
    #    super(User, self).__init__(*args, **kwargs)
    #    self.roles.append(Role.query.filter(Role.name == 'student').first())
    #    db.session.commit()

    @property
    def is_anonymous(self):
        return False

    @property
    def is_teacher(self):
        return "teacher" in [r.name for r in self.roles]

    @property
    def is_admin(self):
        return "admin" in [r.name for r in self.roles]

    @property
    def is_student(self):
        return "student" in [r.name for r in self.roles]

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'email_confirmed_at': str(self.email_confirmed_at).split('.')[0],
            'active': self.active,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'roles': [ro.name for ro in self.roles]
        }

    @property
    def documents_i_can_edit(self):
        if self.is_anonymous:
            return []

        all_docs = Document.query.all()
        docs = []
        if self.is_admin or self.is_teacher:
            docs = all_docs
        else:
            for doc in all_docs:
                if doc.user_id == self.id or (doc.whitelist and self in doc.whitelist.users):
                    if self.is_teacher:
                        docs.append(doc)
                    elif not doc.is_closed:
                        docs.append(doc)
        return docs

    @property
    def documents_from_my_whitelists(self):
        if self.is_anonymous:
            return []

        docs = []
        for doc in Document.query.all():
            if doc.whitelist:
                if self in doc.whitelist.users:
                    docs.append(doc)
        return docs


class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(), nullable=False, server_default='Whitelist')

    users = db.relationship("User", secondary=association_whitelist_has_user, backref=db.backref('whitelists'))

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'users': [u.serialize() for u in self.users]
        }


class AlignmentDiscours(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id', ondelete='CASCADE'))
    speech_part_type_id = db.Column(db.Integer, db.ForeignKey("speech_part_type.id", ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ptr_start = db.Column(db.Integer)
    ptr_end = db.Column(db.Integer)
    note = db.Column(db.Text)

    transcription = db.relationship("Transcription")
    speech_part_type = db.relationship("SpeechPartType")
    user = db.relationship("User")

    def serialize(self):
        return {
            'id': self.id,
            'transcription_id': self.transcription_id,
            'speech_part_type': self.speech_part_type.serialize(),
            'user_id': self.user_id,
            'ptr_start': self.ptr_start,
            'ptr_end': self.ptr_end,
            'note': self.note
        }

def set_notes_from_content(notes_holder):
    """ find notes used in content and assign it to the container
    """
    dom = BeautifulSoup(notes_holder.content, "html.parser")
    notes_ids  = (note_element['id'] for note_element in dom.find_all('adele-note'))
    notes_holder.notes = set(Note.query.filter(Note.id.in_(notes_ids)).all())
