# Contains the redirects
from flask import Flask, render_template, redirect, request, url_for
from server import app

@app.route("/")
def index():
	return render_template("home_page.html")

@app.route("/admin_login")
def admin_login():
	return render_template("index.html")

@app.route("/student_page")
def student_page():
	return render_template("student_page.html")
