from flask.views import MethodView
from flask import jsonify
from webargs.flaskparser import use_args
from marshmallow import Schema, fields
from flask_security import current_user, auth_token_required
import json
from inc.db import db
from sqlalchemy import exc
from inc.util import sendResetCode, getUserToken
#models
from models.user_model import UserModel

# add args
generate_token_args = {
	'email': fields.Email(required=True),
	'password': fields.Str(required=True)
}

class AuthRoute(MethodView):
	@use_args(generate_token_args, locations=('json', 'form'))
	def post(self, args):
		email = args['email']
		password = args['password']
		if email and password:
			token = getUserToken(email,password)
			if token == '-1':
				return jsonify({'error': True, 'messages': {'confirmation': 'Email requires confirmation.'}}), 401
			elif token == '0':
				return jsonify({'error': True, 'messages': {'invalid': 'Incorrect email or password'}}), 401
			else:
				return jsonify({'error': False, 'messages': {}, 'token': token}), 200
		else:
			return jsonify({'error': True, 'messages': {'missing': 'Required field is missing'}}), 422


#add args
req_reset_args = {
	'email': fields.Email(required=True)
}
change_pass_args = {
	'email': fields.Email(required=True),
	'password': fields.Str(required=True),
	'code': fields.Str(required=True)
}
# Reset Password Route
class ResetPasswordRoute(MethodView):
	@use_args(req_reset_args, locations=('query',))
	def get(self, args):
		try:
			email = args['email']
			send_code = sendResetCode(email=email)
			if send_code == 1:
				return jsonify({'error': False, 'messages': {'status': 'Check your email for the secret code'}}), 200
			elif send_code == -1:
				return jsonify({'error': True, 'messages': {'wait': 'You must wait 10 minute to rqeuest another code'}}), 401
			else:
				return jsonify({'error': False, 'messages': {'status': 'Check your email for the secret code'}}), 200
		except SMTPException as emailE:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503

	@use_args(change_pass_args, locations=('form', 'json'))
	def put(self, args):
		try:
			email = args['email']
			password = args['password']
			code = args['code']
			if email and password and code:
				user = UserModel.query.filter_by(email=email,confirmation_code=code).first()
				if user:
					user.password = encrypt_password(password)
					user.confirmation_code = ''
					db.session.commit()
					return jsonify({'error': False, 'messages': {'success': 'Password successfully changed'}}), 200
				else:
					return jsonify({'error': True, 'messages': {'failed': 'Information does not match'}}), 401
			else:
				return jsonify({'error': True, 'messages': {'missing': 'Required field is missing'}}), 422
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503
