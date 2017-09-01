# Contains the redirects
from flask import Flask, render_template, redirect, request, url_for, flash, session
from server import app, user_details
import csv, json, os

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
def admin_tools():
	if 'user' not in session:
		flash('You are not logged in')
		return redirect(url_for("admin_login"))
	elif session['user'] == user_details.get('username'):
		return render_template("admin_tools.html")
	else:
		return "You are not authorized to view this page"

@app.route("/logout")
def logout():
	session.pop('user', None)
	return redirect(url_for('index'))

@app.route("/create_questions", methods = ["POST", "GET"])
def create_questions():
	# Need to check that the admin is in the session
	if 'user' not in session:
		flash('You are not logged in')
		return redirect(url_for("admin_login"))
	elif session['user'] == user_details.get('username'):
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
			return redirect(url_for("create_questions"))
		return render_template("create_questions.html")

@app.route("/view_questions")
def view_questions():
	if os.path.isfile('questions.txt'):
		with open('questions.txt') as f:
			question_entered = json.load(f)
	else:
		question_entered = ['No questions entered']
	return render_template("view_questions.html", all_questions = question_entered)

@app.route("/survey_creation")
def survey_creation():

	return render_template("survey_creation.html")