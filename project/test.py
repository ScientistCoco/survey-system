from flask import Flask, render_template, request
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path = '/static')
app.config["SECRET_KEY"] = "survey-system-w09a-pistachios"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///survey_database.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
	__tablename__ = 'login_details'
	username = db.Column('id', db.String(50), primary_key = True)
	password = db.Column('password', db.String(50))
	type = db.Column('type', db.String(50))

	def get_id(self):
		return str(self.username)

@login_manager.user_loader
def load_user(username):
	return User.query.filter_by(username = username).first()
