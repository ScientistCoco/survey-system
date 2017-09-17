from flask import flash
import os, json, csv, random, sqlite3
from mvc import Controller, SurveyModel, SurveyView
controller = Controller()

class Login:
	def __init__(self, username, password):
		self._username = username
		self._password = password

	# Creates the database for the login username and password
	def _get_login_file(self):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS login_details (id text primary key not null, password text not null, type text not null);") # use your column names here

		with open('passwords.csv','r') as f:
    # csv.DictReader uses first line in file for column headings by default
			dr = csv.DictReader(f)
			to_db = [(i['id'], i['password'], i['type']) for i in dr]
		cur.executemany("INSERT OR REPLACE INTO login_details (id, password, type) VALUES (?, ?, ?);", to_db)
		con.commit()
		con.close()

	def authenticate(self):
		self._get_login_file()
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		# We want to check that the username and password matches the one in the database
		cur.execute("SELECT EXISTS(SELECT * FROM login_details WHERE id = ? and password = ?)", (self._username, self._password))

		if cur.fetchone()[0] == 1:
			con.close()
			return True
		else:
			con.close()
			return False

#test = Login('997', 'student975')
#print(test.authenticate())
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

	def delete_question(self, question_to_delete):
		question_id = controller.search_questionID(question_to_delete)
		controller.delete_question(question_id)

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
