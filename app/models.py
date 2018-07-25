import datetime
from flask import current_app
from flask_login import AnonymousUserMixin
from flask_user import UserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from sqlalchemy import ForeignKeyConstraint

from app import db

association_document_has_acte_type = db.Table('document_has_acte_type',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('type_id', db.Text, db.ForeignKey('acte_type.id'), primary_key=True)
)
association_document_has_editor = db.Table('document_has_editor',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('editor_id', db.Integer, db.ForeignKey('editor.id'), primary_key=True)
)
association_document_has_language = db.Table('document_has_language',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('lang_code', db.String, db.ForeignKey('language.code'), primary_key=True)
)
association_document_has_tradition = db.Table('document_has_tradition',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('tradition_id', db.String, db.ForeignKey('tradition.id'), primary_key=True)
)
association_document_from_country = db.Table('document_from_country',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('country_id', db.Integer, db.ForeignKey('country.id'), primary_key=True)
)
association_document_from_district = db.Table('document_from_district',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('district_id', db.Integer, db.ForeignKey('district.id'), primary_key=True)
)
association_user_has_role = db.Table('user_has_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)
association_document_linked_to_document = db.Table('document_linked_to_document',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('linked_doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
)
association_whitelist_has_user = db.Table('whitelist_has_user',
    db.Column('whitelist_id', db.Integer, db.ForeignKey('whitelist.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
)


class ActeType(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String)
    description = db.Column(db.String)

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'description': self.label
        }


class AlignmentImage(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id', ondelete='CASCADE'), primary_key=True)
    user_id = db.Column(db.Integer,  primary_key=True)
    zone_id = db.Column(db.Integer,  primary_key=True)
    manifest_url = db.Column(db.String,  primary_key=True)
    canvas_idx = db.Column(db.Integer,  primary_key=True)
    img_idx = db.Column(db.Integer,  primary_key=True)

    ptr_transcription_start = db.Column(db.Integer)
    ptr_transcription_end = db.Column(db.Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ("user_id", "zone_id", "manifest_url", "canvas_idx", "img_idx"),
            ["image_zone.user_id", "image_zone.zone_id", "image_zone.manifest_url", "image_zone.canvas_idx", "image_zone.img_idx"],
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

    def serialize(self):
        return {
            'id' : self.id,
            'ref': self.ref,
            'label': self.label
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
    type_id = db.Column(db.Integer, db.ForeignKey('commentary_type.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.Text)

    notes = db.relationship("CommentaryHasNote", back_populates="commentary", cascade="all, delete-orphan", passive_deletes=True)
    type = db.relationship("CommentaryType", backref="commentary")

    def serialize(self):

        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'user_id': self.user_id,
            'type': self.type.serialize(),
            'content': self.content,
            'notes': [
                dict({"ptr_start": n.ptr_start, "ptr_end": n.ptr_end}, **(n.note.serialize()))
                for n in self.notes
            ]
        }


class CommentaryHasNote(db.Model):
    commentary_id = db.Column(db.Integer, db.ForeignKey('commentary.id', ondelete='CASCADE'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), primary_key=True)
    ptr_start = db.Column(db.Integer)
    ptr_end = db.Column(db.Integer)
    note = db.relationship("Note", back_populates="commentary")
    commentary = db.relationship("Commentary", back_populates="notes")


class District(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'country_id': self.country_id
        }


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(), nullable=False, unique=False)
    subtitle = db.Column(db.String(), nullable=False, unique=False)
    creation = db.Column(db.Integer)
    creation_lab = db.Column(db.String())
    copy_year = db.Column(db.String())
    copy_cent = db.Column(db.Integer)
    pressmark = db.Column(db.String())
    argument = db.Column(db.Text())
    date_insert = db.Column(db.String())
    date_update = db.Column(db.String())
    date_closing = db.Column(db.String())
    is_published = db.Column(db.Boolean())
    institution_id = db.Column(db.Integer(), db.ForeignKey("institution.id"))
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id", ondelete='CASCADE'))
    whitelist_id = db.Column(db.Integer(), db.ForeignKey("whitelist.id"))

    # Relationships #
    whitelist = db.relationship("Whitelist", primaryjoin="Document.whitelist_id==Whitelist.id", backref=db.backref('documents'))
    user = db.relationship("User", primaryjoin="Document.user_id==User.id", backref=db.backref('documents'))

    images = db.relationship("Image", primaryjoin="Document.id==Image.doc_id",
        backref=db.backref('document'),
        cascade="all, delete-orphan", single_parent=True,  passive_deletes=True
    )

    institution = db.relationship("Institution", primaryjoin="Document.institution_id==Institution.id", backref=db.backref('documents'))
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
                                       primaryjoin=(association_document_linked_to_document.c.doc_id==id),
                                       secondaryjoin=(association_document_linked_to_document.c.linked_doc_id==id))

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'creation': self.creation,
            'creation_lab': self.creation_lab,
            'copy_year': self.copy_year,
            'copy_cent': self.copy_cent,
            'pressmark': self.pressmark,
            'argument': self.argument,
            'date_insert': self.date_insert,
            'date_update': self.date_update,
            'date_closing': self.date_closing,
            'is_published': self.is_published,
            'institution': self.institution.serialize() if self.institution is not None else None,
            'images': [im.serialize() for im in self.images],
            'acte_types': [at.serialize() for at in self.acte_types],
            'countries': [co.serialize() for co in self.countries],
            'districts': [di.serialize() for di in self.districts],
            'editors': [ed.serialize() for ed in self.editors],
            'languages': [lg.serialize() for lg in self.languages],
            'traditions': [tr.serialize() for tr in self.traditions],
            'whitelist': self.whitelist.serialize() if self.whitelist is not None else None
        }


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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    zone_type_id = db.Column(db.Integer, db.ForeignKey('image_zone_type.id', ondelete='CASCADE'))
    coords = db.Column(db.String)
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
            'canvas_idx' : self.canvas_idx,
            'img_idx' : self.img_idx,
            'zone_id' : self.zone_id,
            'user_id' : self.user_id,
            'zone_type': self.zone_type.serialize(),
            'coords' : self.coords,
            'note' : self.note
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
    canvas_idx = db.Column(db.Integer,  primary_key=True)
    img_idx = db.Column(db.Integer,  primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'))

    zones = db.relationship("ImageZone",
                            primaryjoin="and_(ImageZone.manifest_url == Image.manifest_url, ImageZone.canvas_idx == Image.canvas_idx, ImageZone.img_idx == Image.img_idx)",
                            cascade="all, delete-orphan", passive_deletes=True)
    _image_url = db.relationship("ImageUrl",
                                 primaryjoin="and_(ImageUrl.manifest_url == Image.manifest_url,ImageUrl.canvas_idx == Image.canvas_idx, ImageUrl.img_idx == Image.img_idx)",
                                 uselist=False,
                                 cascade="all, delete-orphan", passive_deletes=True)

    #doc = db.relationship("Document", primaryjoin="Document.id==Image.doc_id",
    #                            backref=db.backref('images'), cascade="all, delete-orphan", single_parent=True, passive_deletes=True)

    @property
    def url(self):
        return self._image_url.img_url

    def serialize(self):
        return {
            'canvas_idx': self.canvas_idx,
            'img_idx': self.img_idx,
            'doc_id': self.doc_id,
            'manifest_url': self.manifest_url,
            'zones': [
                {
                    "zone_id": z.zone_id,
                    "user_id": z.user_id,
                    "coords": z.coords,
                    "note": z.note

                } for z in self.zones
            ],
            'url': self.url
        }


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

    transcription = db.relationship("TranscriptionHasNote", back_populates="note", cascade="all, delete-orphan", passive_deletes=True)
    translation = db.relationship("TranslationHasNote", back_populates="note", cascade="all, delete-orphan", passive_deletes=True)
    commentary = db.relationship("CommentaryHasNote", back_populates="note", cascade="all, delete-orphan", passive_deletes=True)

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            "note_type": self.note_type.serialize()
        }


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
    lang_code = db.Column(db.String, db.ForeignKey("language.code"))
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

    def serialize(self):
        return {
            'id': self.id,
            'label': self.label
        }


class TranscriptionHasNote(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id', ondelete='CASCADE'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), primary_key=True)
    ptr_start = db.Column(db.Integer)
    ptr_end = db.Column(db.Integer)
    note = db.relationship("Note", back_populates="transcription", cascade="all, delete-orphan",single_parent=True)
    transcription = db.relationship("Transcription", back_populates="notes", cascade="all, delete-orphan", single_parent=True)


class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.Text)

    notes = db.relationship("TranscriptionHasNote", back_populates="transcription", cascade="all, delete-orphan", passive_deletes=True)

    def serialize(self):

        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'user_id': self.user_id,
            'content': self.content,
            'notes': [
                dict({"ptr_start": n.ptr_start, "ptr_end": n.ptr_end}, **(n.note.serialize()))
                for n in self.notes
            ]
        }


class TranslationHasNote(db.Model):
    translation_id = db.Column(db.Integer, db.ForeignKey('translation.id', ondelete='CASCADE'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id', ondelete='CASCADE'), primary_key=True)
    ptr_start = db.Column(db.Integer)
    ptr_end = db.Column(db.Integer)
    note = db.relationship("Note", back_populates="translation", cascade="all, delete-orphan", single_parent=True)
    translation = db.relationship("Translation", back_populates="notes", cascade="all, delete-orphan", single_parent=True)


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    content = db.Column(db.Text)

    notes = db.relationship("TranslationHasNote", back_populates="translation", cascade="all, delete-orphan", passive_deletes=True)

    def serialize(self):
        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'user_id': self.user_id,
            'content': self.content,
            'notes': [
                dict({"ptr_start": n.ptr_start, "ptr_end": n.ptr_end}, **(n.note.serialize()))
                for n in self.notes
            ]
        }


class AnonymousUser(AnonymousUserMixin):
    @property
    def documents_i_can_edit(self):
        return []

# Define the User data model
class User(db.Model, UserMixin):
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

    #def __init__(self, *args, **kwargs):
    #    super(User, self).__init__(*args, **kwargs)
    #    self.roles.append(Role.query.filter(Role.name == 'student').first())
    #    db.session.commit()

    @property
    def is_teacher(self): return self.has_roles("teacher")

    @property
    def is_admin(self): return self.has_roles("admin")

    @property
    def is_student(self): return self.has_roles("student")

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

    def generate_auth_token(self, expiration=3600*24):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    @property
    def documents_i_can_edit(self):
        all_docs = Document.query.all()
        docs = []
        if self.is_anonymous:
            return []
        if self.is_admin:
            docs = all_docs
        else:
            for doc in all_docs:
                if doc.user_id == self.id or (doc.whitelist and self in doc.whitelist.users):
                    if self.is_teacher:
                        docs.append(doc)
                    else:
                        if doc.date_closing:
                            # check the closing date
                            now = datetime.datetime.now()
                            doc_closing_time = datetime.datetime.strptime(doc.date_closing, '%Y-%m-%d %H:%M:%S')
                            if now > doc_closing_time:
                                pass
                                #print("document edition is closed")
                            else:
                                docs.append(doc)
                            pass
                        else:
                            docs.append(doc)
        return docs


class UserInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # UserInvitation email information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False)
    # save the user of the invitee
    invited_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


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
