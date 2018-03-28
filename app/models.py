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

class Country(db.Model):
    ref = db.Column(db.String, primary_key=True)
    label = db.Column(db.String)
    def serialize(self):
        return {
            'ref': self.ref,
            'label': self.label
        }

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String)
    country_ref = db.Column(db.String, db.ForeignKey('country.ref'))
    def serialize(self):
        return {
            'code': self.code,
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
            'acte_types': [at.serialize() for at in self.acte_types]
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

class Tradition(db.Model):
    id = db.Column(db.String, primary_key=True)
    label = db.Column(db.String)
    def serialize(self):
        return {
            'id': self.id,
            'label': self.name
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

# Define the Role DataModel
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), unique=True)

## Define the UserRoles DataModel
#class UserHasRole(db.Model):
#    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
#    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)


