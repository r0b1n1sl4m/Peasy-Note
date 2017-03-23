from flask.views import MethodView
from flask import jsonify
from webargs.flaskparser import use_args
from marshmallow import Schema, fields
from inc.db import db
from sqlalchemy import exc
from flask_security import SQLAlchemyUserDatastore, auth_token_required, current_user, confirmable
from flask_security.utils import encrypt_password
from smtplib import SMTPException
from inc.util import sendVerificationCode
import datetime
#models
from models.user_model import UserModel, RoleModel
from models.user_info_model import UserInfoModel

# add args
create_user_args = {
	'first_name': fields.Str(required=True),
	'last_name': fields.Str(required=True),
	'email': fields.Email(required=True),
	'password': fields.Str(required=True),
	'age': fields.Integer(missing=None),
	'profession': fields.Str(missing=None)
}
update_user_args = {
	'first_name': fields.Str(required=True),
	'last_name': fields.Str(required=True),
	'age': fields.Integer(missing=None),
	'profession': fields.Str(missing=None)
}

#define schema
class UserInfoSchema(Schema):
	id = fields.Integer(attribute="user_id")
	first_name = fields.Str()
	last_name = fields.Str()
	email = fields.Email()
	age = fields.Integer()
	profession = fields.Str()

# define data store
user_datastore = SQLAlchemyUserDatastore(db, UserModel, RoleModel)
class UserRoute(MethodView):

	@auth_token_required
	def get(self):
		try:
			if not current_user:
				return jsonify({'error': True, 'messages': {'status': 'Could not retrive any information'}}), 404
			else:
				user_info = current_user.info.first()
				result = UserInfoSchema().dump(user_info)
				return jsonify({'error': False, 'messages': {}, 'results': result.data}), 200
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503

	@use_args(create_user_args, locations=('json', 'form'))
	def post(self, args):
		try:
			first_name = args['first_name']
			last_name = args['last_name']
			email = args['email']
			password = args['password']
			age = args['age']
			profession = args['profession']
			if email and password and first_name and last_name:
				exuser = UserModel.query.filter_by(email=email).first()
				if not exuser:
					password = encrypt_password(password)
					user = user_datastore.create_user(email=email, password=password)
					user_info = UserInfoModel(first_name=first_name, last_name=last_name, age=age,profession=profession, email=email)
					user.info.append(user_info)
					db.session.commit()
					result = UserInfoSchema().dump(user_info)
					try:
						send_code = sendVerificationCode(email=email)
						status = 'Verification email has been sent'
					except SMTPException as emailE:
						status = 'Unable to sent verification email request another email'
					return jsonify({'error': False, 'messages': {'status': status}, 'results': result.data}), 200
				else:
					return jsonify({'error': True, 'messages': {'exists': 'User already exists try to login'}}), 422
			else:
				return jsonify({'error': True, 'messages': {'missing': 'Required field is missing'}}), 422
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503

	@auth_token_required
	@use_args(update_user_args, locations=('json', 'form'))
	def put(self, args):
		try:
			first_name = args['first_name']
			last_name = args['last_name']
			age = args['age']
			profession = args['profession']
			if first_name and last_name:
				user_info = current_user.info.first()
				user_info.first_name = first_name
				user_info.last_name = last_name
				user_info.age = age
				user_info.profession = profession
				db.session.commit()
				result = UserInfoSchema().dump(user_info)
				return jsonify({'error': False, 'results': result.data}), 200
			else:
				return jsonify({'error': True, 'messages': {'missing': 'Required field is missing'}}), 422
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503

# Request Confirmation Code Route
# add args
request_code_args = {
	'email': fields.Email(required=True)
}
class ReqConRoute(MethodView):
	@use_args(request_code_args, locations=('query',))
	def get(self, args):
		try:
			email = args['email']
			send_code = sendVerificationCode(email=email)
			if send_code == 1:
				return jsonify({'error': False, 'messages': {'status': 'Verification code sent successfully'}}), 200
			elif send_code == -1:
				return jsonify({'error': True, 'messages': {'wait': 'You must wait 5 minute to rqeuest another code'}}), 401
			elif send_code == 2:
				return jsonify({'error': True, 'messages': {'confirmed': 'This account is already confirmed'}}), 200
			else:
				return jsonify({'error': False, 'messages': {'status': 'Verification code sent successfully'}}), 200
		except SMTPException as emailE:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503

# Verify Confirmation Code Route
#add args
con_code_args = {
	'email': fields.Email(required=True),
	'code': fields.Str(required=True)
}
class VerifyConRoute(MethodView):
	@use_args(con_code_args, locations=('query',))
	def get(self, args):
		try:
			email = args['email']
			code = args['code']
			user = UserModel.query.filter_by(email=email,confirmation_code=code).first()
			if user:
				user.confirmed_at = datetime.datetime.now()
				user.confirmation_code = ''
				db.session.commit()
				return jsonify({'error': False, 'messages': {'confirmed': 'You have successfully verified your email'}}), 200
			else:
				return jsonify({'error': True, 'messages': {'failed': 'Information does not match'}}), 401
		except exc.IntegrityError as e:
			return jsonify({'error': True, 'messages': {'internel': 'Something went wrong please try again later'}}), 503
