from flask import Flask, session
app = Flask(__name__)
app.config["SECRET_KEY"] = "survey-system-w09a-pistachios"

user_details = {'username': 'Admin', 'password': 'password'}