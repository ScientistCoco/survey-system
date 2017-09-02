# Contains the redirects
from flask import Flask, render_template, redirect, request, url_for, flash, session
from server import app, user_details
import csv, json, os
from functools import wraps

# Make a function decorater to check if the user is an admin
def check_is_admin(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if 'user' not in session:
			flash('You are not logged in')
			return redirect(url_for("admin_login"))
		else:
			return f(*args, **kwargs)
	return wrapper

@app.route("/")
def index():
	return render_template("home_page.html")

@app.route("/admin_login", methods = ["POST", "GET"])
def admin_login():
	if request.method == "POST":
		# Get the data that the user entered
		session['user'] = request.form["user_name"]
		password_entered = request.form["password"]

		# Then check that the user has entered the correct details
		# If correct then redirect to the admin tool page
		# Else show a message that login failed and allow them to try again
		if session['user'] in user_details.get('username') and password_entered in user_details.get('password'):
			return redirect(url_for("admin_tools"))
		else:
			flash('You failed to login, try again')
			return redirect(url_for("admin_login"))

	return render_template("login_page.html")

@app.route("/student_page")
def student_page():
	return render_template("student_page.html")

@app.route("/admin_tools", methods = ["POST", "GET"])
@check_is_admin
def admin_tools():
	if session['user'] == user_details.get('username'):
		return render_template("admin_tools.html")
	else:
		return "You are not authorized to view this page"

@app.route("/logout")
def logout():
	session.pop('user', None)
	return redirect(url_for('index'))

@app.route("/create_questions", methods = ["POST", "GET"])
@check_is_admin
def create_questions():
	# If the user chooses to submit a question we need to save it
	# to a csv file and flash a message to show that the question
	# was saved to a file
	if request.method == "POST":
		# Check if the questions file exists, if it does we 
		# grab the data which is in json format and convert
		# it to a list type
		if os.path.isfile('questions.txt'):
			with open('questions.txt') as f:
				question_entered = json.load(f)
		else:
			question_entered = []
		# Read the input from the server and append to the list
		# Then dump the question list back into the file
		input_from_server = request.form.getlist('question_entered')
		question_entered = question_entered + input_from_server
		question_entered = json.dumps(question_entered)
		with open('questions.txt', 'w') as f:
			f.write(question_entered)
		flash('Question successfully saved')
		f.close()
		return redirect(url_for("create_questions"))
	return render_template("create_questions.html")

@app.route("/view_questions")
@check_is_admin
def view_questions():
	question_entered = checking_question_file_exists()
	return render_template("view_questions.html", all_questions = question_entered)

@app.route("/survey_creation", methods = ["POST", "GET"])
@check_is_admin
def survey_creation():
	course_list = []
	list_of_question_for_course = []
	survey_from_file = {}
	selected_course = ''
	# Transferring the course.csv file into a list so that we can parse it
	# to javascript and display a dropdown menu of the courses available 
	with open('courses.csv', 'r') as course_file:
		reader = csv.reader(course_file)
		course_file = list(reader)
		del course_file[0]
	for course in course_file:
		course_list = course_list + course
	# Then get the list of questions that we made in the create_questions directory
	question_entered = checking_question_file_exists()

	if request.method == "POST":
		if os.path.isfile('survey_course.txt'):
			f = open('survey_course.txt', 'r')
			survey_from_file = json.load(f)
			f.close()
		# Gathering the post data on the selected course and selected question
		selected_course = request.form.get('course')
		selected_question = request.form.get('question')

		# Check if the selected course already has a survey made, if it does
		# we add the questions to that course survey, if not we make a new
		# dictionary key for that course
		if selected_course in survey_from_file:
			list_of_question_for_course = survey_from_file[selected_course]
			# We check if the question has already been added to the survey form:
			if selected_question in list_of_question_for_course:
				flash('Question already added')
			else:
				list_of_question_for_course = survey_from_file[selected_course] + [selected_question]
			survey_from_file[selected_course] = list_of_question_for_course
		else:
			survey_from_file.update({selected_course:[selected_question]})
		f = open('survey_course.txt', 'w')
		survey_to_file = json.dumps(survey_from_file)
		f.write(survey_to_file)
		f.close()
		#flash('Question added to the survey')
	return render_template("survey_creation.html", course_list = course_list,
		question_list = question_entered, questions_added = list_of_question_for_course,
		course_url = selected_course)


# Function to check that the question file exists
def checking_question_file_exists():
	if os.path.isfile('questions.txt'):
		with open('questions.txt') as f:
			question_entered = json.load(f)
	else:
		question_entered = ['No questions entered']
	return question_entered

@app.route("/answer_survey/<course>", methods = ['GET', 'POST'])
def answer_survey(course):
	#Load the survey json file which contains the course and their respective questions
	if os.path.isfile('survey_course.txt'):
		f = open('survey_course.txt', 'r')
		survey_from_file = json.load(f)
		f.close()
		if course not in survey_from_file:
			return "No surveys have been created"
	else:
		return "No surveys have been created"

	return render_template("survey_form.html", course_survey = survey_from_file[course], course_name = course) 