from flask import Flask, render_template, request, url_for, redirect, current_app
from classes import Survey_system, Student, Staff, Admin, Teacher, Database
from flask_login import LoginManager, login_required, login_user, UserMixin, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__, static_url_path = '/static')
app.config["SECRET_KEY"] = "survey-system-w09a-pistachios"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey_database.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Create the database
database = Database()
database.create_tables()
database.create_student_enrolments_table()
database.create_survey_availability_table()
database.login_details_loader()

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
				return render_template('invalid_access.html')
				#return current_app.login_manager.unauthorized()
			# Then we check the type of the user
			if ((current_user.type != role) and (role != "ANY")):
				return render_template('invalid_access.html')
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
		elif current_user.type == 'admin' :
			return redirect(url_for('dashboard'))
		elif current_user.type == 'staff':
			return redirect(url_for('staff_dashboard'))
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
				student = Student(registered_user.get_id())
				survey_system = Survey_system('courses.csv', student)
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
	admin = Admin(current_user.get_id())
	survey_system = Survey_system('courses.csv', admin)
	results = admin.get_survey_availabilities()
	return render_template('dashboard.html', open = results[0], close = results[1], null = results[2],
courses_open = admin.list_of_courses_status('open'))

@app.route("/responses", methods = ["POST", "GET"])
def responses():
	if current_user.get_type() == 'student':
		student = Student(current_user.get_id())
		survey_system = Survey_system('courses.csv', student)

		courses = student.get_courses()
		course_list = []
		# Then get the courses that are closed
		for course in courses:
			if survey_system.get_status_of_course(course + ' ' +student.get_semester()) == 'close':
				course_list.append(course + ' ' + student.get_semester())
	else:
		admin = Admin(current_user.get_id())
		survey_system = Survey_system('courses.csv', admin)
		course_list = admin.list_of_courses_status('close')

	if request.method == "POST":
		# Get the questions associated with the survey
		# Then determine if the question is MC or short answer
		# If MC then we get the answers and make a chart
		course_name = request.form.get('course_selected')
		MC_responses = survey_system.get_MC_responses(course_name)

		return render_template('responses.html', course_list = course_list, MC_responses = MC_responses,
	course_name = course_name)

	return render_template('responses.html', course_list = course_list)

@app.route("/sa_responses_<course_name>", methods = ["POST", "GET"])
def sa_responses(course_name):
	admin = Admin(current_user.get_id())
	survey_system = Survey_system('courses.csv', admin)
	sa_results = survey_system.get_SA_responses(course_name)

	if request.method == "POST":
		question_text = request.form.get('q_selected')
		return render_template('sa_responses.html', course_name = course_name, q_list = sa_results, a_list = sa_results[question_text], question = question_text)
	return render_template('sa_responses.html', course_name = course_name, q_list = sa_results)

@app.route("/staff_dashboard", methods = ["POST", "GET"])
@login_required(role = "staff")
def staff_dashboard():
	teacher = Teacher(current_user.get_id())
	survey_system = Survey_system('courses.csv', teacher)
	courses = teacher.get_surveys_to_review()

	if request.method == "POST":
		course_name = request.form.get('course_name')
		return redirect(url_for('review_course', course_name = course_name))
	return render_template('staff_dashboard.html', course_list = courses)

@app.route("/student_dashboard", methods = ["POST", "GET"])
@login_required(role = "student")
def student_dashboard():
	student = Student(current_user.get_id())
	survey_system = Survey_system('courses.csv', student)
	#database.add_info_enrollments()
	courses = student.get_courses()
	semester = student.get_semester()

	if request.method == "POST":
		course_name = request.form.get('course_name')
		course_semester = course_name + ' ' + semester
		return redirect(url_for('answer_survey', course_name = course_name, semester = semester))
	return render_template('student_page.html', course_list = courses, semester = semester)

@app.route("/review_<course_name>", methods = ["POST", "GET"])
@login_required(role = 'staff')
def review_course(course_name):
	teacher = Teacher(current_user.get_id())
	survey_system = Survey_system('courses.csv', teacher)
	question_answer = {}
	question_in_course = survey_system.get_question(course_name)

	for question in question_in_course:
		question_answer[question] = teacher.view_answers(question)

	if request.method == "POST":
		if (request.form.getlist('question-selected')):
			selected_question = request.form.get('question-selected')
			teacher.add_question_to_course(selected_question, course_name)
			status = teacher.get_course_status(course_name)
			# Update the question list
			question_in_course = survey_system.get_question(course_name)
			for question in question_in_course:
				question_answer[question] = teacher.view_answers(question)

		elif request.form['submit'] == 'open':
			selected_course = request.form.get('course_selected')
			teacher.pass_review(selected_course)
			status = teacher.get_course_status(selected_course)
			return redirect(url_for('staff_dashboard'))

		elif request.form['submit'] == 'delete_question':
			selected_course = request.form.get('course_selected')
			question_to_delete = request.form.getlist('checkbox_value')
			for question in question_to_delete:
				teacher.delete_question_from_course_teacher(question, course_name)

			# Refresh the question_answer list
			question_answer = {}
			question_in_course = survey_system.get_question(course_name)
			for question in question_in_course:
				question_answer[question] = teacher.view_answers(question)

	return render_template('review_survey.html', course_name = course_name, question_answer = question_answer,
question_list = teacher.view_questions(), status = teacher.get_course_status(course_name))

@app.route("/question", methods = ["POST", "GET"])
@login_required(role = "admin")
def question_page():
	admin = Admin(current_user.get_id())
	survey_system = Survey_system('courses.csv', admin)

	question_from_server = []
	answer_list = []
	error = 'negative'
	if request.method == "POST":
		if request.form['submit'] == 'add_question':
			question_from_server = request.form.get('question_entered')
			answer_list = request.form.getlist('answer_entered[]')
			question_type = request.form.get('QType')
			if len(answer_list) == 1 and question_type == 'MC':	# If user does add MC options
				error = 'positive'
			else:	# If the user did not pick an option for question_type then default is SA
				if not question_type:
					if len(answer_list) > 1:
						question_type = 'MC'
					else:
						question_type = 'SA'
				admin.add_question(question_from_server, question_type, answer_list)

		elif request.form['submit'] == 'delete_question':
			question_to_delete = request.form.getlist('checkbox_value')
			for question in question_to_delete:
				admin.delete_question(question)
			# Returns a list of the options selected
	question_answer = {}
	question_list = admin.view_questions()
	for question in question_list:
		question_answer[question] = admin.view_answers(question)
	return render_template('question_page.html', question_answer = question_answer, error = error)

selected_course = ''
@app.route("/survey_creation", methods = ["POST", "GET"])
@login_required(role = "admin")
def survey_creation():
	admin = Admin(current_user.get_id())
	survey_system = Survey_system('courses.csv', admin)

	if request.method == "POST":
	#if (request.form.get('course-selected')):
		question_answer = {}
		if request.form.get('course-selected'):
			selected_course = request.form.get('course-selected')
			question_in_course = survey_system.get_question(selected_course)

			for question in question_in_course:
				list1 = ()
				list1 = list1 + admin.get_mandatory_status(selected_course, question) + admin.view_answers(question)
				question_answer[question] = list1
			status = survey_system.get_status_of_course(selected_course)

		elif request.form['submit'] == 'open':
			selected_course = request.form.get('course_selected')
			status = survey_system.get_status_of_course(selected_course)
			admin.change_survey_status(selected_course, status)
			status = survey_system.get_status_of_course(selected_course)

		elif (request.form.getlist('question-selected')):
			selected_course = request.form.get('course_selected')
			selected_question = request.form.get('question-selected')
			# Check the question has not already been added:
			check = admin.check_for_duplicates(selected_course, selected_question)
			if (check == 0):	# Question not yet added
				admin.add_question_to_course(selected_question, selected_course)
			status = survey_system.get_status_of_course(selected_course)
			# Update the question list
			question_in_course = survey_system.get_question(selected_course)
			for question in question_in_course:
				list1 = ()
				list1 = list1 + admin.get_mandatory_status(selected_course, question) + admin.view_answers(question)
				question_answer[question] = list1

		elif request.form['submit'] == 'delete_question':
			selected_course = request.form.get('course_selected')
			question_to_delete = request.form.getlist('checkbox_value')
			for question in question_to_delete:
				admin.delete_question_from_course(question, selected_course)
			# Update the question_answer dictionary
			question_answer = {}
			question_in_course = survey_system.get_question(selected_course)

			for question in question_in_course:
				list1 = ()
				list1 = list1 + admin.get_mandatory_status(selected_course, question) + admin.view_answers(question)
				question_answer[question] = list1
			status = survey_system.get_status_of_course(selected_course)

		elif request.form['submit'] == 'put_into_review':
			selected_course = request.form.get('course_selected')
			mandatory_questions = request.form.getlist('checkbox_value')
			admin.push_mandatory_questions(selected_course, mandatory_questions)
			admin.change_survey_status(selected_course, 'review')
			status = survey_system.get_status_of_course(selected_course)

		return render_template("survey_creation.html", course_list = survey_system.get_course_list(),
			question_list = admin.view_questions(), question_answer = question_answer,
			course_selected = selected_course, status = status)

	return render_template("survey_creation.html", course_list = survey_system.get_course_list(),
		question_list = admin.view_questions())

@app.route("/answer_survey/<course_name> <semester>", methods = ["POST", "GET"])
@login_required(role = "student")
def answer_survey(course_name, semester):
	student = Student(current_user.get_id())
	survey_system = Survey_system('courses.csv', student)
	question_answer = {}

	# Check that the student is part of the course before they can answer survey
	if course_name in student.get_courses() and semester in student.get_semester():
		# Check that surveys for that course exist, if it doesn't return an error message
		questions = survey_system.get_question(course_name + ' ' + semester)
		if not questions:
			status = 'has no surveys'
		else:
			# If there are questions we check that the student has not answered the survey before:
			if student.check_if_survey_completed(course_name) == 'yes':
				status = 'survey already completed'
			else:
			# If there are questions, we want to check that the survey is open for answers
				if survey_system.get_status_of_course(course_name + ' ' + semester) == 'open':
					# we want to find the answers then make a dictionary
					# so that the answer and question are related
					status = 'open'

					for question in questions:
						question_answer[question] = student.view_answers(question)

					if request.method == "POST":
						for k in question_answer:
							answer = request.form.get(k)
							student.submit_answers(course_name + ' ' + semester, k, answer)
						# Then we update the database to indicate the student has completed the survey
						student.survey_completed(course_name)
						return redirect(url_for('student_dashboard'))
				else:
					status = 'survey is closed'
	else:
		status = 'Not part of the course to answer survey'
	return render_template("survey_form.html", course_name = course_name, semester = semester,
	question_answer = question_answer, status = status)


from routes import app
app.run(debug=True)
