import csv, json, os
from flask import Flask, request, flash

class Admin:
	def __init__(self, username, password, course, question_file, course_file):
		self.username = username
		self.password = password
		self.course = course
		self.question_file = question_file
		self.course_file = course_file

	def create_questions(self):
	# If the user chooses to submit a question we need to save it
	# to a csv file and flash a message to show that the question
	# was saved to a file.
	# Check if the questions file exists, if it does we 
	# grab the data which is in json format and convert
	# it to a list type
		if os.path.isfile(self.question_file):
			with open(self.question_file) as f:
				question_entered = json.load(f)
		else:
			question_entered = []
		input_from_server = request.form.getlist('question_entered')
		question_entered = question_entered + input_from_server
		question_entered = json.dumps(question_entered)
		with open(self.question_file, 'w') as f:
			f.write(question_entered)
		flash('Question successfully saved')
		f.close()

	def view_questions(self):
		pass

	# Checks the question_file exists
	def checking_question_file_exists(self):
		if os.path.isfile(self.question_file):
			with open(self.question_file) as f:
				question_entered = json.load(f)
		else:
			question_entered = ['No questions entered']
		return question_entered

	def create_survey(self, course_list, question_entered, list_of_question_for_course, selected_course, survey_from_file):
		self.course_list = course_list
		self.question_entered = question_entered
		self.list_of_question_for_course = list_of_question_for_course
		self.selected_course = selected_course
		self.survey_from_file = survey_from_file
		# Transferring the course.csv file into a list so that we can parse it
		# to javascript and display a dropdown menu of the courses available 
		with open(self.course_file, 'r') as course_file:
			reader = csv.reader(course_file)
			course_file = list(reader)
			del course_file[0]
		for course in course_file:
			self.course_list = self.course_list + course
		# Then get the list of questions that we made in the create_questions directory
		self.question_entered = self.checking_question_file_exists()

		if request.method == "POST":
			if os.path.isfile('survey_course.txt'):
				f = open('survey_course.txt', 'r')
				survey_from_file = json.load(f)
				f.close()
			# Gathering the post data on the selected course and selected question
			self.selected_course = request.form.get('course')
			self.selected_question = request.form.get('question')

			# Check if the selected course already has a survey made, if it does
			# we add the questions to that course survey, if not we make a new
			# dictionary key for that course
			if self.selected_course in self.survey_from_file:
				self.list_of_question_for_course = self.survey_from_file[selected_course]
				# We check if the question has already been added to the survey form:
				if self.selected_question in self.list_of_question_for_course:
					flash('Question already added')
				else:
					self.list_of_question_for_course = self.survey_from_file[self.selected_course] + [self.selected_question]
				self.survey_from_file[selected_course] = self.list_of_question_for_course
			else:
				self.survey_from_file.update({self.selected_course:[self.selected_question]})
			f = open('survey_course.txt', 'w')
			survey_to_file = json.dumps(self.survey_from_file)
			f.write(survey_to_file)
			f.close()
			#flash('Question added to the survey')	

