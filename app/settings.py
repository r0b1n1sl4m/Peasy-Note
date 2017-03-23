# configuration
class Config():
	DEBUG = False
	#wtf from
	WTF_CSRF_ENABLED = False
	#db
	SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/notes'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	#security
	SECRET_KEY = 'super-secret'
	SECURITY_PASSWORD_HASH = 'sha512_crypt'
	SECURITY_PASSWORD_SALT = '63c3nt'
	SECURITY_TOKEN_MAX_AGE = 40000
	SECURITY_CONFIRMABLE = True
	SECURITY_CONFIRM_LOGIN_WITHOUT_CONFIRMATION = False
	SECURITY_EMAIL_SENDER = 'contact@codefairbd.com'
	#mail configuration
	MAIL_SERVER = 'srv1.example.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = 'contact@codefairbd.com'
	MAIL_PASSWORD = 'password'
	MAIL_DEFAULT_SENDER = 'contact@codefairbd.com'