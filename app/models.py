from app import Base, engine, name_for_collection_relationship

from sqlalchemy import Table, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, backref


association_document_has_act_type = Table('document_has_acte_type', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.doc_id')),
    Column('type_id', Text, ForeignKey('acte_type.type_id'))
)
association_document_has_editor = Table('document_has_editor', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.doc_id')),
    Column('editor_name', Text, ForeignKey('editor.editor_name'))
)
association_document_has_language = Table('document_has_language', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.doc_id')),
    Column('lang_code', Text, ForeignKey('language.lang_code'))
)
association_document_has_tradition = Table('document_has_tradition', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.doc_id')),
    Column('tradition_id', Text, ForeignKey('tradition.tradition_id'))
)
association_document_from_country = Table('document_from_country', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.doc_id')),
    Column('country_ref', Text, ForeignKey('country.country_ref'))
)
association_document_from_district = Table('document_from_district', Base.metadata,
    Column('doc_id', Integer, ForeignKey('document.doc_id')),
    Column('district_id', Integer, ForeignKey('district.district_id'))
)


class ActType(Base):
    __tablename__ = 'acte_type'
    type_id = Column(Integer, primary_key=True)
    label = Column(Text)
    description = Column(Text)

class Country(Base):
    __tablename__ = 'country'
    country_ref = Column(Text, primary_key=True)
    country_label = Column(Text)

class District(Base):
    __tablename__ = 'district'
    district_id = Column(Integer, primary_key=True)
    district_label = Column(Text)
    country_ref = Column(Text)

class Document(Base):
    __tablename__ = 'document'
    doc_id = Column(Integer, primary_key=True)
    title = Column(Text)
    subtitle = Column(Text)
    creation = Column(Integer)
    creation_lab = Column(Text)
    copy_year = Column(Text)
    copy_cent = Column(Text)
    institution_ref = Column(Text, ForeignKey('institution.instit_ref'))
    pressmark = Column(Text)
    argument = Column(Text)
    date_insert = Column(Text)
    date_update = Column(Text)
    institution = relationship("Institution",
                               backref=backref('Document', lazy=True))
    act_types = relationship("ActType",
                             secondary=association_document_has_act_type,
                             primaryjoin=(association_document_has_act_type.c.doc_id == doc_id))
    countries = relationship("Country",
                            secondary=association_document_from_country)
    districts = relationship("District",
                             secondary=association_document_from_district,
                             primaryjoin=(association_document_from_district.c.doc_id == doc_id))
    editors = relationship("Editor",
                             secondary=association_document_has_editor)
    languages = relationship("Language",
                             secondary=association_document_has_language)
    traditions = relationship("Tradition",
                             secondary=association_document_has_tradition)

class Editor(Base):
    __tablename__ = 'editor'
    editor_ref = Column(Text)
    editor_name = Column(Text, primary_key=True)

class Institution(Base):
    __tablename__ = 'institution'
    instit_ref = Column(Text, primary_key=True)
    instit_name = Column(Text)

class Language(Base):
    __tablename__ = 'language'
    lang_code = Column(Text, primary_key=True)
    lang_label = Column(Text)

class Tradition(Base):
    __tablename__ = 'tradition'
    tradition_id = Column(Text, primary_key=True)
    tradition_label = Column(Text)

