from flask import current_app
from flask_mail import Message
import random
from models.user_model import UserModel
import datetime
from inc.db import db
from smtplib import SMTPException
from flask_security.utils import encrypt_password, verify_password

def sendMail(email, rand):
	mail = current_app.extensions.get('mail')
	msg = Message(subject="Peasy Notes Verification Code")
	msg.add_recipient(email)
	msg.html = "<p>Your verification code for peasy notes is: <strong>"+rand+"</strong></p><p>Please ignore this email if you have not requested for any verification code</p>"
	mail.send(msg)

def sendVerificationCode(email):
	user = UserModel.query.filter_by(email=email).first()
	if user:
		confirmed_date = user.confirmed_at
		if not confirmed_date:
			req_date = user.requested_at
			last_req = [-1,-1]
			if req_date:
				last_req = datetime.datetime.now() - req_date
				last_req = divmod(last_req.days * 86400 + last_req.seconds, 60)
			if last_req[0]==-1 or last_req[0]>5:
				#send mail
				rand = str(random.randint(1111,9999))
				sendMail(email,rand)
				#update database
				user.requested_at = datetime.datetime.now()
				user.confirmation_code = rand
				db.session.commit()
				return 1
			else:
				return -1
		else:
			return 2
	else:
		return 0

def sendResetCode(email):
	user = UserModel.query.filter_by(email=email).first()
	if user:
		req_date = user.requested_at
		last_req = [-1,-1]
		if req_date:
			last_req = datetime.datetime.now() - req_date
			last_req = divmod(last_req.days * 86400 + last_req.seconds, 60)
		if last_req[0]==-1 or last_req[0]>10:
			#send mail
			rand = str(random.randint(1111,9999))
			sendMail(email,rand)
			#update database
			user.requested_at = datetime.datetime.now()
			user.confirmation_code = rand
			db.session.commit()
			return 1
		else:
			return -1
	else:
		return 0

def getUserToken(email,password):
	user = UserModel.query.filter_by(email=email).first()
	if user and verify_password(password, user.password):
		if user.confirmed_at:
			return user.get_auth_token()
		else:
			return '-1'
	else:
		return '0'
	