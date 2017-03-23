from inc.db import db, BaseModel
from flask_security import UserMixin, RoleMixin
from models.notes_model import NotesModel
from models.user_info_model import UserInfoModel

# Define models
roles_users = db.Table('roles_users', 
	db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
	db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class RoleModel(BaseModel, RoleMixin):
	__tablename__ = 'role'
	name = db.Column(db.String(80), unique=True, nullable=False)
	description = db.Column(db.String(255))

class UserModel(BaseModel, UserMixin):
	__tablename__ = 'user'
	email = db.Column(db.String(255), unique=True, nullable=False)
	password = db.Column(db.String(255), nullable=False)
	active = db.Column(db.Boolean())
	confirmation_code = db.Column(db.String(4))
	requested_at = db.Column(db.DateTime())
	confirmed_at = db.Column(db.DateTime())
	info = db.relationship('UserInfoModel', backref="user", cascade="all, delete-orphan", single_parent=True, lazy='dynamic')
	notes = db.relationship('NotesModel', backref="owner", cascade="all, delete-orphan", single_parent=True, lazy='dynamic')
	roles = db.relationship('RoleModel', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))