from flask import flash
import os, json, csv, random, sqlite3
from mvc import Controller, SurveyModel, SurveyView
controller = Controller()

class StudentDatabase():

	def add_info_enrollments(self):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS student_enrolments (id int not null, course_name text not null, semester text not null, survey_completed text not null, num int primary key not null);") # use your column names here

		with open('enrolments.csv','r') as f:
     # csv.DictReader uses first line in file for column headings by default
			dr = csv.DictReader(f)
			increment = 0;
			for i in dr:
				increment = increment + 1
				to_db = [(i['id'], i['course_name'], i['semester'],'no', increment)]
				cur.executemany("INSERT OR REPLACE INTO student_enrolments (id, course_name, semester, survey_completed, num) VALUES (?, ?, ?, ?, ?);", to_db)
				con.commit()
		con.close()

	def get_student_courses(self, id):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		rows = cur.execute("SELECT course_name FROM student_enrolments WHERE id = ?", (id,))
		student_courses = []
		for row in rows:
			student_courses = student_courses + list(row)
		con.close()
		return student_courses

	def get_student_semester(self, id):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		cur.execute("SELECT semester FROM student_enrolments WHERE id = ?", (id,))
		semester = cur.fetchone()
		con.close()
		return semester[0]

	def completion_of_survey(self, id, course_name):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		cur.execute("UPDATE student_enrolments SET survey_completed = 'yes' WHERE id = ? AND course_name = ?", (id, course_name))
		con.commit()
		con.close()

	def check_if_survey_completed(self, id, course_name):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()

		cur.execute("SELECT survey_completed FROM student_enrolments WHERE id = ? AND course_name = ?", (id, course_name))
		result = cur.fetchone()
		con.close()
		return result[0]

class SurveyAvailability():
	# Create the survey_availability table if it doesn't exist
	def add_info(self):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		cur.execute("CREATE TABLE IF NOT EXISTS survey_availability (course_name text primary key not null, availability text);")

		with open('courses.csv','r') as f:
     # csv.DictReader uses first line in file for column headings by default
			reader = csv.reader(f)
			for field in reader:
				text = field[0] + ' ' + field[1]
				cur.execute("INSERT OR REPLACE INTO survey_availability (course_name) VALUES ('%s');" %(text))
				con.commit()
		con.close()

class Admin:
	def __init__(self):
		pass

	def open_questionfile(self):
		questions = controller.view_all_questions()
		return questions

	def add_question(self, question_to_add, answer_to_add, questionType):
		questionID = random.randint(1,50)
		answerID = questionID
		controller.add_questionText(questionID, question_to_add, questionType)
		for answer in answer_to_add:
			controller.add_answerText(answerID, questionID, answer)

	def view_answers(self, question_to_see):
		question_id = controller.search_questionID(question_to_see)
		answer_list = controller.search_answerText(question_id)
		return answer_list

	def delete_question(self, question_to_delete):
		question_id = controller.search_questionID(question_to_delete)
		controller.delete_question(question_id)

	def get_survey_availabilities(self):
		survey_open = controller.count_survey_status('open')
		survey_close = controller.count_survey_status('close')
		survey_null = controller.count_survey_status('null')
		availability = [survey_open, survey_close, survey_null]
		return availability

	def surveys_to_review(self):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		rows = cur.execute("SELECT course_name FROM survey_availability WHERE availability = 'review'")
		courses = []
		for row in rows:
			courses = courses + list(row)
		con.close()
		return courses

	def list_of_courses_status(self, status):
		courses = controller.list_of_courses_status(status)
		return courses

admin = Admin()
print(admin.list_of_courses_status('null'))
class Survey(Admin):
	def __init__(self, course_filename):
		Admin.__init__(self)
		self.course_filename = course_filename

	def search_for_course_questions(self, course_name):
		questions = []
		questions = controller.search_surveyID(course_name)
		return questions

	def get_courselist(self):
		course_list = []
		f = open(self.course_filename)
		reader = csv.reader(f)
		for row in reader:
			course_list = course_list + [" ".join(row)]
		return course_list

	def get_survey_status(self, course_name):
		result = controller.get_survey_status(course_name)
		return result

	def change_survey_status(self, course_name, status):
		controller.change_survey_status(course_name, status)

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

admin = Admin()
print(admin.get_survey_availabilities())
