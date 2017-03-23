from flask.views import MethodView
from flask import jsonify
from webargs.flaskparser import use_args
from marshmallow import Schema, fields
from inc.db import db
from sqlalchemy import exc
from flask_security import SQLAlchemyUserDatastore, auth_token_required, current_user
#models
from models.notes_model import NotesModel

# add args
create_note_args = {
	'title': fields.Str(required=True),
	'desc': fields.Str(missing=None)
}

#define schema
class NotesGetSchema(Schema):
	id = fields.Integer()
	title = fields.Str()
	desc = fields.Str()

class NotesRoute(MethodView):
	@auth_token_required
	def get(self, note_id):
		try:
			if note_id is None:
				notes = current_user.notes.all()
				result = NotesGetSchema(many=True).dump(notes).data
				return jsonify({'error': False, 'count': len(notes), 'results': result}), 200
			else:
				note = NotesModel.query.filter_by(id=note_id,user_id=current_user.id).first()
				if note:
					result = NotesGetSchema().dump(note).data
					return jsonify({'error': False, 'results': result}), 200
				else:
					return jsonify({'error': True, 'messages': {'404': 'Could not find any note'}}), 404
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503

	@auth_token_required
	@use_args(create_note_args, locations=('json', 'form'))
	def post(self, args):
		try:
			title = args['title']
			desc = args['desc']
			if title:
				note = NotesModel(title=title,desc=desc,user_id=current_user.id)
				db.session.add(note)
				db.session.commit()
				result = NotesGetSchema().dump(note).data
				return jsonify({'error': False, 'results': result}), 200
			else:
				return jsonify({'error': True, 'messages': {'missing': 'Required field is missing'}}), 422
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503

	@auth_token_required
	@use_args(create_note_args, locations=('json', 'form'))
	def put(self, args, note_id):
		try:
			title = args['title']
			desc = args['desc']
			if title:
				note = NotesModel.query.filter_by(id=note_id,user_id=current_user.id).first()
				if note:
					note.title = title
					if desc:
						note.desc = desc
					db.session.commit()
					result = NotesGetSchema().dump(note).data
					return jsonify({'error': False, 'results': result}), 200
				else:
					return jsonify({'error': True, 'messages': {'404': 'Could not find any note to update'}}), 404
			else:
				return jsonify({'error': True, 'messages': {'missing': 'Required field is missing'}}), 422
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503

	@auth_token_required
	def delete(self, note_id):
		try:
			note = NotesModel.query.filter_by(id=note_id,user_id=current_user.id).first()
			if note:
				db.session.delete(note)
				db.session.commit()
				return jsonify({'error': False}), 200
			else:
				return jsonify({'error': True, 'messages': {'404': 'Could not find any note to delete'}}), 404
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503


