from app import Base, engine, name_for_collection_relationship

from sqlalchemy import Table, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, backref


association_document_has_act_type = Table('document_has_acte_type', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.id')),
    Column('type_id', Text, ForeignKey('acte_type.id'))
)
association_document_has_editor = Table('document_has_editor', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.id')),
    Column('editor_id', Text, ForeignKey('editor.id'))
)
association_document_has_language = Table('document_has_language', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.id')),
    Column('lang_code', Text, ForeignKey('language.code'))
)
association_document_has_tradition = Table('document_has_tradition', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.id')),
    Column('tradition_id', Text, ForeignKey('tradition.id'))
)
association_document_from_country = Table('document_from_country', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.id')),
    Column('country_ref', Text, ForeignKey('country.ref'))
)
association_document_from_district = Table('document_from_district', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.id')),
    Column('district_id', Integer, ForeignKey('district.id'))
)


class ActType(Base):
    __tablename__ = 'acte_type'
    id = Column(Integer, primary_key=True)
    label = Column(Text)
    description = Column(Text)
    def serialize(self):
        return {
            'id': self.id,
            'label': self.label,
            'description': self.label
        }

class Country(Base):
    __tablename__ = 'country'
    ref = Column(Text, primary_key=True)
    label = Column(Text)
    def serialize(self):
        return {
            'ref': self.ref,
            'label': self.label
        }

class District(Base):
    __tablename__ = 'district'
    id = Column(Integer, primary_key=True)
    label = Column(Text)
    country_ref = Column(Text)
    def serialize(self):
        return {
            'code': self.code,
            'label': self.label,
            'country_ref': self.country_ref
        }

class Document(Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    subtitle = Column(Text)
    creation = Column(Integer)
    creation_lab = Column(Text)
    copy_year = Column(Text)
    copy_cent = Column(Text)
    institution_ref = Column(Text, ForeignKey('institution.ref'))
    pressmark = Column(Text)
    argument = Column(Text)
    date_insert = Column(Text)
    date_update = Column(Text)
    institution = relationship("Institution",
                               backref=backref('Document', lazy=True))
    act_types = relationship("ActType",
                             secondary=association_document_has_act_type,
                             primaryjoin=(association_document_has_act_type.c.doc_id == id))
    countries = relationship("Country",
                            secondary=association_document_from_country)
    districts = relationship("District",
                             secondary=association_document_from_district,
                             primaryjoin=(association_document_from_district.c.doc_id == id))
    editors = relationship("Editor",
                             secondary=association_document_has_editor)
    languages = relationship("Language",
                             secondary=association_document_has_language)
    traditions = relationship("Tradition",
                             secondary=association_document_has_tradition)
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
            'date_insert': self.pressmark,
            'date_update': self.pressmark,
            'institution': self.institution.serialize(),
            'act_types': [at.serialize() for at in self.act_types]
        }

class Editor(Base):
    __tablename__ = 'editor'
    id = Column(Integer, primary_key=True)
    ref = Column(Text)
    name = Column(Text)
    def serialize(self):
        return {
            'ref': self.ref,
            'name': self.name
        }

class Institution(Base):
    __tablename__ = 'institution'
    ref = Column(Text, primary_key=True)
    name = Column(Text)
    def serialize(self):
        return {
            'ref': self.ref,
            'name': self.name
        }

class Language(Base):
    __tablename__ = 'language'
    code = Column(Text, primary_key=True)
    label = Column(Text)
    def serialize(self):
        return {
            'code': self.code,
            'label': self.label
        }

class Tradition(Base):
    __tablename__ = 'tradition'
    id = Column(Text, primary_key=True)
    label = Column(Text)
    def serialize(self):
        return {
            'id': self.id,
            'label': self.name
        }

