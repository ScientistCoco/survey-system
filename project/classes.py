from flask import flash
import os, json, csv, random
from mvc import Controller, SurveyModel, SurveyView
controller = Controller()
class Login:
	def __init__(self, username, password):
		self._username = username
		self._password = password

	def authenticate(self, **user_details):
		if self._username == user_details['username'] and self._password == user_details['password']:
			return True
		else:
			return False

class Admin:

	def __init__(self, question_filename):
		self.question_filename = question_filename

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

class Survey(Admin):
	def __init__(self, survey_filename, question_filename, course_filename):
		Admin.__init__(self, question_filename)
		self.survey_filename = survey_filename
		self.course_filename = course_filename

	def open_surveyfile(self):
		survey_file = {}
		if os.path.isfile(self.survey_filename):
			with open(self.survey_filename) as f:
				survey_file = json.load(f)
			f.close()
		return survey_file

	def get_courselist(self):
		course_list = []
		f = open(self.course_filename)
		reader = csv.reader(f)
		courses_from_file = list(reader)
		del courses_from_file[0]
		for course in courses_from_file:
			course_list = course_list + course
		return course_list


	def add_question_to_survey(self, course_name, question_to_add):
		question_list = super(Survey, self).open_questionfile()
		survey_dict = self.open_surveyfile()
		course_list = self.get_courselist()

		if course_name in survey_dict:
			if question_to_add[0] not in survey_dict[course_name]:
				survey_dict[course_name].append(question_to_add[0])
			else:
				flash('Question already added')
		else:
			survey_dict[course_name] = question_to_add

		with open(self.survey_filename, 'w') as f:
			survey_dict = json.dumps(survey_dict)
			f.write(survey_dict)
			f.close()

	def get_questions_in_course(self, course_name):
		survey_dict = self.open_surveyfile()
		if course_name in survey_dict:
			return survey_dict[course_name]
		else:
			return []

	def get_answers_to_questions(self, question_list):
		question_answer = {}
		for question in question_list:
			question_answer[question] = super(Survey, self).view_answers(question)
		return question_answer
