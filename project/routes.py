from flask import Flask, render_template, request, session, url_for, redirect
from classes import Login, Admin, Survey

app = Flask(__name__, static_url_path = '/static')
app.config["SECRET_KEY"] = "survey-system-w09a-pistachios"

user_details = {'username': 'Admin', 'password': 'password'}

admin = Admin('question_file.txt')

@app.route("/", methods = ["POST","GET"])
def index():
	if request.method == "POST":
		session['user'] = request.form['user_name']
		password_entered = request.form['password']
		login_id = Login(session['user'], password_entered)

		if login_id.authenticate(**user_details) == True:
			return redirect(url_for('dashboard'))
		else:
			return 'Bad'
	return render_template('index_page.html')

@app.route("/dashboard")
def dashboard():
	return render_template('dashboard.html')

@app.route("/question", methods = ["POST", "GET"])
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
def survey_creation():
	survey = Survey('survey_course.txt', 'question_file.txt', 'courses.csv')

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

#@app.route('/get_course_questions')
from routes import app
app.run(debug=True)
