from flask import flash
import os, json, csv, random, sqlite3
from mvc import Controller, SurveyModel, SurveyView
controller = Controller()

class Admin:

	def __init__(self):
		pass

	def open_questionfile(self):
		questions = controller.view_all_questions()
		return questions

	def add_question(self, question_to_add, answer_to_add):
		questionID = random.randint(1,50)
		answerID = questionID
		controller.add_questionText(questionID, question_to_add)
		for answer in answer_to_add:
			controller.add_answerText(answerID, questionID, answer)

	def view_answers(self, question_to_see):
		question_id = controller.search_questionID(question_to_see)
		answer_list = controller.search_answerText(question_id)
		return answer_list

	def delete_question(self, question_to_delete):
		question_id = controller.search_questionID(question_to_delete)
		controller.delete_question(question_id)

class Survey(Admin):
	def __init__(self, course_filename):
		Admin.__init__(self)
		self.course_filename = course_filename

	def open_surveyfile(self):
		survey_file = {}
		if os.path.isfile(self.survey_filename):
			with open(self.survey_filename) as f:
				survey_file = json.load(f)
			f.close()
		return survey_file

	def search_for_course_questions(self, course_name):
		questions = []
		questions = controller.search_surveyID(course_name)
		return questions

	def get_courselist(self):
		course_list = []
		f = open(self.course_filename)
		reader = csv.reader(f)
		courses_from_file = list(reader)
		for course in courses_from_file:
			course_list = course_list + course
		return course_list


	def add_question_to_survey(self, course_name, question_to_add):
		#First find id of the question_to_add
		question_id = controller.search_questionID(question_to_add)
		controller.add_to_survey(course_name, question_id)

	def get_questions_in_course(self, course_name):
		all_questions = controller.search_surveyID(course_name)
		return all_questions

	def get_answers_to_questions(self, question_list):
		question_answer = {}
		for question in question_list:
			question_answer[question] = super(Survey, self).view_answers(question)
		return question_answer

	def delete_question_from_survey(self, question_to_delete, course_name):
		question_id = controller.search_questionID(question_to_delete)
		controller.delete_question_from_survey(question_id, course_name)

class StudentAnswers:
	def init(self):
		pass

	def add_answers(self, course_name, question, answer_picked):
		questionID = controller.search_questionID(question)
		controller.add_to_answer_database(course_name, questionID, answer_picked)
