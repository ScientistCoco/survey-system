# Contains the redirects
from flask import Flask, render_template, redirect, request, url_for, flash, session
from server import app, user_details

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
		return "You are not logged in"
	elif session['user'] == user_details.get('username'):
		if request.method == "POST":
			session.pop('user', None)
			return redirect(url_for('index'))
		return render_template("admin_tools.html")
	else:
		return "You are not authorized to view this page"
