from flask_user import UserMixin

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
    db.Column('country_ref', db.String, db.ForeignKey('country.ref'), primary_key=True)
)
association_document_from_district = db.Table('document_from_district',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('district_id', db.Integer, db.ForeignKey('district.id'), primary_key=True)
)
association_user_has_role = db.Table('user_has_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

association_commentary_has_note = db.Table('commentary_has_note',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('type_id', db.Integer, db.ForeignKey('commentary_type.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
    db.Column('ptr_start', db.Integer),
    db.Column('ptr_end', db.Integer),
)
association_document_linked_to_document = db.Table('document_linked_to_document',
    db.Column('doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
    db.Column('linked_doc_id', db.Integer, db.ForeignKey('document.id'), primary_key=True),
)

class ActeType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)
    description = db.Column(db.String)
    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'description': self.label
        }

class AlignmentDiscours(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), primary_key=True)
    ptr_start = db.Column(db.Integer, primary_key=True)
    ptr_end = db.Column(db.Integer, primary_key=True)
    speech_part_type_id = db.Column(db.Integer, db.ForeignKey("speech_part_type.id"))
    def serialize(self):
        return {
            'transcription_id': self.transcription_id,
            'note_id': self.note_id,
            'ptr_start': self.ptr_start,
            'ptr_end': self.ptr_end,
            'speech_part_type_id': self.speech_part_type_id,
        }

class AlignmentImage(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id'), primary_key=True)
    manifest_url = db.Column(db.String, db.ForeignKey('image_zone.manifest_url'), primary_key=True)
    img_id = db.Column(db.Integer, db.ForeignKey('image_zone.img_id'), primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('image_zone.zone_id'), primary_key=True)
    def serialize(self):
        return {
            'transcription_id': self.transcription_id,
            'manifest_url': self.manifest_url,
            'img_id': self.img_id,
            'zone_id': self.zone_id
        }

class AlignmentTranslation(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id'), primary_key=True)
    translation_id = db.Column(db.Integer, db.ForeignKey('translation.id'), primary_key=True)
    ptr_transcription_start = db.Column(db.Integer, primary_key=True)
    ptr_transcription_end = db.Column(db.Integer, primary_key=True)
    ptr_translation_start = db.Column(db.Integer, primary_key=True)
    ptr_translation_end = db.Column(db.Integer, primary_key=True)
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
    ref = db.Column(db.String, primary_key=True)
    label = db.Column(db.String)
    def serialize(self):
        return {
            'ref': self.ref,
            'label': self.label
        }

class CommentaryType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)
    def serialize(self):
        return {
            'id': self.ref,
            'label': self.label
        }

class Commentary(db.Model):
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id'), primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('commentary_type.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    content = db.Column(db.Text)

    notes = db.relationship("Note", secondary=association_commentary_has_note,
                             primaryjoin=(association_commentary_has_note.c.doc_id == doc_id and
                                          association_commentary_has_note.c.type_id == type_id and
                                          association_commentary_has_note.c.user_id == user_id),
                             backref=db.backref('commentary'))


    def serialize(self):
        return {
            'doc_id': self.doc_id,
            'type_id': self.type_id,
            'user_id': self.user_id,
            'content': self.content,
            'notes': [n.serialize() for n in self.notes]
        }

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)
    country_ref = db.Column(db.String, db.ForeignKey('country.ref'))
    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'country_ref': self.country_ref
        }

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False, unique=False)
    subtitle = db.Column(db.String(), nullable=False, unique=False)
    creation = db.Column(db.Integer, nullable=False)
    creation_lab = db.Column(db.String())
    copy_year = db.Column(db.String())
    copy_cent = db.Column(db.Integer)
    institution_ref = db.Column(db.String(), db.ForeignKey('institution.ref'))
    pressmark = db.Column(db.String())
    argument = db.Column(db.Text())
    date_insert = db.Column(db.String())
    date_update = db.Column(db.String())

    # Relationships#
    images = db.relationship("Image", primaryjoin="Document.id==Image.doc_id", backref='document')
    institution = db.relationship("Institution", backref=db.backref('document', lazy=True))
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
            'title': self.title,
            'creation': self.creation,
            'creation_lab': self.creation_lab,
            'copy_year': self.copy_year,
            'copy_cent': self.copy_cent,
            'pressmark': self.pressmark,
            'argument': self.argument,
            'date_insert': self.date_insert,
            'date_update': self.date_update,
            'institution': self.institution.serialize() if self.institution is not None else None,
            'images': [im.serialize() for im in self.images],
            'acte_types': [at.serialize() for at in self.acte_types],
            'countries': [co.serialize() for co in self.countries],
            'districts': [di.serialize() for di in self.districts],
            'editors': [ed.serialize() for ed in self.editors],
            'languages': [lg.serialize() for lg in self.languages],
            'traditions': [tr.serialize() for tr in self.traditions]
        }

class Editor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref = db.Column(db.String)
    name = db.Column(db.String)
    def serialize(self):
        return {
            'ref': self.ref,
            'name': self.name
        }

class Image(db.Model):
    manifest_url = db.Column(db.String, primary_key=True)
    id = db.Column(db.String, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    def serialize(self):
        return {
            'id': self.id,
            'doc_id': self.doc_id,
            'manifest_url': self.manifest_url
        }

class ImageZone(db.Model):
    manifest_url = db.Column(db.String, db.ForeignKey('image.zone'), primary_key=True)
    img_id = db.Column(db.String, db.ForeignKey('image.id'), primary_key=True)
    zone_id = db.Column(db.Integer, primary_key=True)
    coords = db.Column(db.String)
    note = db.Column(db.String)

    def serialize(self):
        return {
            'manifest_url': self.manifest_url,
            'img_id' : self.img_id,
            'zone_id' : self.zone_id,
            'coords' : self.coords,
            'note' : self.note
        }

class Institution(db.Model):
    ref = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    def serialize(self):
        return {
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
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('note_type.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)

    note_type = db.relationship("NoteType")

    transcriptions = db.relationship("TranscriptionHasNote", back_populates="note")
    translations = db.relationship("TranslationHasNote", back_populates="note")

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            "note_type": self.note_type.serialize()
        }

class NoteType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)
    def serialize(self):
        return {
            'id': self.id,
            'label': self.label
        }

# Define the Role DataModel
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
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
    id = db.Column(db.String, primary_key=True)
    lang_code = db.Column(db.String, db.ForeignKey("language.code"), primary_key=True)
    label = db.Column(db.String)
    definition = db.Column(db.Text)

class Tradition(db.Model):
    id = db.Column(db.String, primary_key=True)
    label = db.Column(db.String)
    def serialize(self):
        return {
            'id': self.id,
            'label': self.label
        }

class TranscriptionHasNote(db.Model):
    transcription_id = db.Column(db.Integer, db.ForeignKey('transcription.id'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), primary_key=True)
    ptr_start = db.Column(db.Integer)
    ptr_end = db.Column(db.Integer)
    note = db.relationship("Note", back_populates="transcriptions")
    transcription = db.relationship("Transcription", back_populates="notes")


class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)

    notes = db.relationship("TranscriptionHasNote", back_populates="transcription")

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
    translation_id = db.Column(db.Integer, db.ForeignKey('translation.id'), primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), primary_key=True)
    ptr_start = db.Column(db.Integer)
    ptr_end = db.Column(db.Integer)
    note = db.relationship("Note", back_populates="translations")
    translation = db.relationship("Translation", back_populates="notes")


class Translation(db.Model):
    id = db.Column(db.String, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)

    notes = db.relationship("TranslationHasNote", back_populates="translation")

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

# Define the User data model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False, server_default='')

    # User email information
    email = db.Column(db.String(), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column('firstname', db.String(), nullable=False, server_default='')
    last_name = db.Column('lastname', db.String(), nullable=False, server_default='')

    # Relationships
    roles = db.relationship('Role', secondary=association_user_has_role,
            backref=db.backref('users', lazy='dynamic'))

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'confirmed_at': self.confirmed_at,
            'active': self.active,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'roles': [ro.name for ro in self.roles]
        }


