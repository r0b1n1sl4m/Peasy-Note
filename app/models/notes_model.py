from inc.db import db, BaseModel

class NotesModel(BaseModel):
	__tablename__ = 'notes'
	title = db.Column(db.String(255), nullable=False)
	desc = db.Column(db.Text)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))