from inc.db import db
class UserInfoModel(db.Model):
	__tablename__ = 'user_info'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False)
	first_name = db.Column(db.String(55), nullable=False)
	last_name = db.Column(db.String(55), nullable=False)
	age = db.Column(db.Integer)
	profession = db.Column(db.String(255))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))