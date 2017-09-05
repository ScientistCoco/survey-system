# Contains the redirects
from flask import Flask, render_template, redirect, request, url_for, flash, session
from server import app, user_details
from classes import Admin
import csv, json, os
from functools import wraps

admin_user = Admin('Help', user_details['password'], 'COMP', 'questions.txt', 'courses.csv')

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
		if session['user'] == user_details['username'] and password_entered == user_details['password']:
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
	if request.method == "POST":
		admin_user.create_questions()
		return redirect(url_for("create_questions"))
	return render_template("create_questions.html")

@app.route("/view_questions")
@check_is_admin
def view_questions():
	question_entered = admin_user.checking_question_file_exists()
	return render_template("view_questions.html", all_questions = question_entered)

@app.route("/survey_creation", methods = ["POST", "GET"])
@check_is_admin
def survey_creation():
	course_list = []
	list_of_question_for_course = []
	survey_from_file = {}
	selected_course = ''	
	admin_user.create_survey(course_list, list_of_question_for_course, survey_from_file, selected_course, survey_from_file)
	return render_template("survey_creation.html", course_list = admin_user.course_list,
		question_list = admin_user.question_entered, questions_added = admin_user.list_of_question_for_course,
		course_url = admin_user.selected_course)

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