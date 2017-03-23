from flask import Flask
from flask import jsonify
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_security import Security, SQLAlchemyUserDatastore, login_required
from flask_mail import Mail
from inc.db import db
from marshmallow import Schema, fields
# Import routes
from routes.user_route import UserRoute, ReqConRoute, VerifyConRoute, user_datastore
from routes.auth_route import AuthRoute, ResetPasswordRoute
from routes.notes_route import NotesRoute

app = Flask(__name__)
app.config.from_object('settings.Config')

# initialization
db.init_app(app)
mail = Mail(app)
security = Security(app, user_datastore, register_blueprint=False)

# migration
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# adding routes
# user
app.add_url_rule('/api/user/', view_func=UserRoute.as_view('user_api'), methods=['POST', 'GET', 'PUT'])
app.add_url_rule('/api/user/request_confirmation/', view_func=ReqConRoute.as_view('req_con_api'), methods=['GET'])
app.add_url_rule('/api/user/confirm/', view_func=VerifyConRoute.as_view('verify_con_api'), methods=['GET'])
#auth
app.add_url_rule('/api/auth/token/', view_func=AuthRoute.as_view('token_api'), methods=['POST'])
app.add_url_rule('/api/auth/reset_password/', view_func=ResetPasswordRoute.as_view('reset_pass_api'), methods=['GET', 'PUT'])
#notes
notes_view = NotesRoute.as_view('notes_api')
app.add_url_rule('/api/notes/', defaults={'note_id': None}, view_func=notes_view, methods=['GET'])
app.add_url_rule('/api/notes/', view_func=notes_view, methods=['POST',])
app.add_url_rule('/api/notes/<int:note_id>/', view_func=notes_view, methods=['GET', 'PUT', 'DELETE'])

# error handlers
@app.errorhandler(422)
def handle_unprocessable_entity(err):
    data = getattr(err, 'data')
    if data:
        messages = data['messages']
        errobj = {}
        for i in messages:
        	errobj[i] = messages[i][0]
        messages = errobj
    else:
        messages = {
        	'request': 'Invalid Request'
        }
    return jsonify({
    	'error': True,
        'messages': messages,
    }), 422

#run
if __name__ == '__main__':
	app.run(host='localhost',threaded=True)
	# manager.run()