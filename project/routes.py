from flask import Flask, render_template, request, url_for, redirect, current_app
from classes import Admin, Survey, StudentAnswers, StudentDatabase
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

	def get_type(self):
		return str(self.type)

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
	# Case for when the user is already logged in
	if current_user.is_authenticated:
		if current_user.type == 'student':
			return redirect(url_for('student_dashboard'))
		elif current_user.type == 'staff' :
			return redirect(url_for('dashboard'))

	# If not logged in
	if request.method == "POST":
		username = request.form['ID']
		password_entered = request.form['password']
		#login_id = Login(session['user'], password_entered)
		registered_user = User.query.filter_by(username = username, password = password_entered).first()
		if registered_user is None:
			return render_template('login_page.html', login_state = 'failed')
		else:
			login_user(registered_user)
			# Then redirect to certain webpage depending on role
			if registered_user.type == 'student':
				return redirect(url_for('student_dashboard'))
			elif registered_user.type == 'staff' :
				return redirect(url_for('staff_dashboard'))
			elif registered_user.type == 'admin' :
				return redirect(url_for('dashboard'))
	return render_template('login_page.html')

@app.route("/logout")
@login_required(role = "ANY")
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route("/dashboard")
@login_required(role = "admin")
def dashboard():
	# We then need to check the type of the user, if its a staff we direct to the
	# staff dashboard, else if its student they go to student dashboard
	results = admin.get_survey_availabilities()
	return render_template('dashboard.html', open = results[0], close = results[1], null = results[2])

@app.route("/staff_dashboard", methods = ["POST", "GET"])
@login_required(role = "staff")
def staff_dashboard():
	courses = admin.surveys_to_review()

	if request.method == "POST":
		course_name = request.form.get('course_name')
		return redirect(url_for('review_course', course_name = course_name))
	return render_template('staff_dashboard.html', course_list = courses)

@app.route("/student_dashboard", methods = ["POST", "GET"])
@login_required(role = "student")
def student_dashboard():
	database = StudentDatabase()
	#database.add_info_enrollments()
	courses = database.get_student_courses(current_user.get_id())
	semester = database.get_student_semester(current_user.get_id())

	if request.method == "POST":
		course_name = request.form.get('course_name')
		course_semester = course_name + ' ' + semester
		return redirect(url_for('answer_survey', course_name = course_name, semester = semester))
	return render_template('student_page.html', course_list = courses, semester = semester)

@app.route("/review_<course_name>", methods = ["POST", "GET"])
@login_required(role = 'staff')
def review_course(course_name):
	survey = Survey('courses.csv')
	question_answer = {}
	question_in_course = survey.get_questions_in_course(course_name)

	for question in question_in_course:
		question_answer[question] = admin.view_answers(question)

	if request.method == "POST":
		if (request.form.getlist('question-selected')):
			selected_question = request.form.get('question-selected')
			survey.add_question_to_survey(course_name, selected_question)
			status = survey.get_survey_status(course_name)
			# Update the question list
			question_in_course = survey.get_questions_in_course(course_name)
			for question in question_in_course:
				question_answer[question] = admin.view_answers(question)

		elif request.form['submit'] == 'open':
			selected_course = request.form.get('course_selected')
			survey.change_survey_status(course_name, '')
			status = survey.get_survey_status(course_name)
			return redirect(url_for('staff_dashboard'))

		elif request.form['submit'] == 'delete_question':
			selected_course = request.form.get('course_selected')
			question_to_delete = request.form.getlist('checkbox_value')
			for question in question_to_delete:
				survey.delete_question_from_survey(question, course_name)
			# Refresh the question_answer list
			question_answer = {}
			question_in_course = survey.get_questions_in_course(course_name)
			for question in question_in_course:
				question_answer[question] = admin.view_answers(question)
		return render_template('review_survey.html', course_name = course_name, question_answer = question_answer,
	question_list = admin.open_questionfile(), status = survey.get_survey_status(course_name))

	return render_template('review_survey.html', course_name = course_name, question_answer = question_answer,
question_list = admin.open_questionfile(), status = survey.get_survey_status(course_name))

@app.route("/question", methods = ["POST", "GET"])
@login_required(role = "ANY")
def question_page():
	question_from_server = []
	answer_list = []
	error = 'negative'
	if request.method == "POST":
		if request.form['submit'] == 'add_question':
			question_from_server = request.form.get('question_entered')
			answer_list = request.form.getlist('answer_entered[]')
			question_type = request.form.get('QType')
			if len(answer_list) == 1 and question_type == 'MC':
				error = 'positive'
			else:
				admin.add_question(question_from_server, answer_list, question_type)
		elif request.form['submit'] == 'delete_question':
			question_to_delete = request.form.getlist('checkbox_value')
			for question in question_to_delete:
				admin.delete_question(question)
			# Returns a list of the options selected
	question_answer = {}
	question_list = admin.open_questionfile()
	for question in question_list:
		question_answer[question] = admin.view_answers(question)
	return render_template('question_page.html', question_answer = question_answer, error = error)

selected_course = ''
@app.route("/survey_creation", methods = ["POST", "GET"])
@login_required(role = "ANY")
def survey_creation():
	survey = Survey('courses.csv')

	if request.method == "POST":
	#if (request.form.get('course-selected')):
		question_answer = {}
		if request.form.get('course-selected'):
			selected_course = request.form.get('course-selected')
			question_in_course = survey.get_questions_in_course(selected_course)

			for question in question_in_course:
				question_answer[question] = admin.view_answers(question)

			status = survey.get_survey_status(selected_course)

		elif request.form['submit'] == 'open':
			selected_course = request.form.get('course_selected')
			status = survey.get_survey_status(selected_course)
			survey.change_survey_status(selected_course, status)
			status = survey.get_survey_status(selected_course)

		elif (request.form.getlist('question-selected')):
			selected_course = request.form.get('course_selected')
			selected_question = request.form.get('question-selected')
			survey.add_question_to_survey(selected_course, selected_question)
			status = survey.get_survey_status(selected_course)
			# Update the question list
			question_in_course = survey.get_questions_in_course(selected_course)
			for question in question_in_course:
				question_answer[question] = admin.view_answers(question)

		elif request.form['submit'] == 'delete_question':
			selected_course = request.form.get('course_selected')
			question_to_delete = request.form.getlist('checkbox_value')
			for question in question_to_delete:
				survey.delete_question_from_survey(question, selected_course)

		elif request.form['submit'] == 'put_into_review':
			selected_course = request.form.get('course_selected')
			survey.change_survey_status(selected_course, 'review')
			status = survey.get_survey_status(selected_course)

		return render_template("survey_creation.html", course_list = survey.get_courselist(),
			question_list = admin.open_questionfile(), question_answer = question_answer,
			course_selected = selected_course, status = status)


	return render_template("survey_creation.html", course_list = survey.get_courselist(),
		question_list = admin.open_questionfile())

@app.route("/answer_survey/<course_name> <semester>", methods = ["POST", "GET"])
def answer_survey(course_name, semester):
	# Check that the student is part of the course
	student_database = StudentDatabase()
	question_answer = {}

	# Check that the student is part of the course before they can answer survey
	if course_name in student_database.get_student_courses(current_user.username) and semester in student_database.get_student_semester(current_user.username):
		# Check that surveys for that course exist, if it doesn't return an error message
		survey = Survey('courses.csv')
		student_answers = StudentAnswers()
		questions = survey.search_for_course_questions(course_name + ' ' + semester)
		if not questions:
			status = 'has no surveys'
		else:
			# If there are questions we check that the student has not answered the survey before:
			if student_database.check_if_survey_completed(current_user.username, course_name) == 'yes':
				status = 'survey already completed'
			else:
			# If there are questions, we want to check that the survey is open for answers
				if survey.get_survey_status(course_name + ' ' + semester) == 'open':
					# we want to find the answers then make a dictionary
					# so that the answer and question are related
					status = 'open'
					question_answer = survey.get_answers_to_questions(questions)
					if request.method == "POST":
						for k in question_answer:
							answer = request.form.get(k)
							student_answers.add_answers(course_name, k, answer)
						# Then we update the database to indicate the student has completed the survey
						student_database.completion_of_survey(current_user.username, course_name)
						return redirect(url_for('student_dashboard'))
				else:
					status = 'survey is closed'
	else:
		status = 'Not part of the course to answer survey'
	return render_template("survey_form.html", course_name = course_name, semester = semester,
	question_answer = question_answer, status = status)


from routes import app
app.run(debug=True)
