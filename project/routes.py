from flask import Flask, render_template, request, url_for, redirect, current_app
from classes import Admin, Survey, StudentAnswers
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__, static_url_path = '/static')
app.config["SECRET_KEY"] = "survey-system-w09a-pistachios"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey_database.db'

db = SQLAlchemy(app)

admin = Admin()
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
	__tablename__ = 'login_details'
	username = db.Column('id', db.String(50), primary_key = True)
	password = db.Column('password', db.String(50))
	type = db.Column('type', db.String(50))

	def get_id(self):
		return str(self.username)

# Making the function decorator to check that user is logged in
# source code: https://stackoverflow.com/questions/15871391/implementing-flask-login-with-multiple-user-classes
def login_required(role = "ANY"):
	def wrapper(fn):
		@wraps(fn)
		def decorated_view(*args, **kwargs):
			if not current_user.is_authenticated:
				return current_app.login_manager.unauthorized()
			# Then we check the type of the user
			if ((current_user.type != role) and (role != "ANY")):
				return current_app.login_manager.unauthorized()
			return fn(*args, **kwargs)
		return decorated_view
	return wrapper

@login_manager.user_loader
def load_user(username):
	return User.query.filter_by(username = username).first()

@app.route("/", methods = ["POST","GET"])
def index():
	if request.method == "POST":
		username = request.form['ID']
		password_entered = request.form['password']
		#login_id = Login(session['user'], password_entered)
		registered_user = User.query.filter_by(username = username, password = password_entered).first()
		if registered_user is None:
			return render_template('login_page.html', login_state = 'failed')
		else:
			login_user(registered_user)
			return redirect(url_for('dashboard'))
	return render_template('login_page.html')

@app.route("/logout")
@login_required(role = "ANY")
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route("/dashboard")
@login_required(role = "staff")
def dashboard():
	# We then need to check the type of the user, if its a staff we direct to the
	# staff dashboard, else if its student they go to student dashboard
	return render_template('dashboard.html')

@app.route("/question", methods = ["POST", "GET"])
@login_required(role = "ANY")
def question_page():
	question_from_server = []
	answer_list = []
	if request.method == "POST":
		if request.form['submit'] == 'add_question':
			question_from_server = request.form.get('question_entered')
			answer_list = request.form.getlist('answer_entered[]')
			admin.add_question(question_from_server, answer_list)
		elif request.form['submit'] == 'delete_question':
			question_to_delete = request.form.getlist('checkbox_value')
			for question in question_to_delete:
				admin.delete_question(question)
			# Returns a list of the options selected
	question_answer = {}
	question_list = admin.open_questionfile()
	for question in question_list:
		question_answer[question] = admin.view_answers(question)
	return render_template('question_page.html', question_answer = question_answer)

selected_course = ''
@app.route("/survey_creation", methods = ["POST", "GET"])
@login_required(role = "ANY")
def survey_creation():
	survey = Survey('courses.csv')

	#if (request.form.get('course-selected')):
	if request.form.getlist('course-selected'):
		selected_course = request.form.get('course-selected')
		question_in_course = survey.get_questions_in_course(selected_course)
		question_answer = {}
		for question in question_in_course:
			question_answer[question] = admin.view_answers(question)
		#question_answer = survey.get_answers_to_questions(question_in_course)
		return render_template("survey_creation.html", course_list = survey.get_courselist(),
			question_list = admin.open_questionfile(), question_answer = question_answer,
			course_selected = selected_course)

	elif (request.form.getlist('question-selected')):
		selected_course = request.form.get('course_selected')
		selected_question = request.form.get('question-selected')
		survey.add_question_to_survey(selected_course, selected_question)

	if request.method == "POST":
		if request.form['submit'] == 'delete_question':
			selected_course = request.form.get('course_selected')
			question_to_delete = request.form.getlist('checkbox_value')
			for question in question_to_delete:
				survey.delete_question_from_survey(question, selected_course)

	return render_template("survey_creation.html", course_list = survey.get_courselist(),
		question_list = admin.open_questionfile())

@app.route("/answer_survey/<course_name>", methods = ["POST", "GET"])
def answer_survey(course_name):
	# First check that surveys for that course exist, if it doesn't return an error message
	question_answer = {}
	survey = Survey('survey_course.txt', 'question_file.txt', 'courses.csv')
	student_answers = StudentAnswers()
	questions = survey.search_for_course_questions(course_name)
	if not questions:
		return 'No surveys for this course'
	else:
		# If there are questions, we want to find the answers then make a dictionary
		# so that the answer and question are related
		question_answer = survey.get_answers_to_questions(questions)
		if request.method == "POST":
			for k in question_answer:
				answer = request.form.get(k)
				student_answers.add_answers(course_name, k, answer)
			return 'Answer Saved'
		return render_template("survey_form.html", course_name = course_name, question_answer = question_answer)


from routes import app
app.run(debug=True)
