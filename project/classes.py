from flask import flash
import os, json, csv, random, sqlite3
from mvc import Controller, SurveyModel, SurveyView
controller = Controller()

class Survey_system():
	def __init__(self, course_filename, user = None):
		self.user = user
		self.course_filename = course_filename

	def get_question(self, course_name):
		# Returns the questions associated with the course
		questions = []
		questions = controller.search_surveyID(course_name)
		return questions

	def get_MC_responses(self, course):
		questions = controller.search_surveyID(course)
		ID = []
		bank = {}
		for question in questions:
			ID.append(controller.search_questionID(question))
		MCQuestions = controller.get_ID_MC_SA(ID, 'MC')

		# Now we find the answers associated with the MCQuestions
		for x in MCQuestions:
			outer_key = list(controller.search_answerText(x))
			question_text = controller.find_question(x)
			ansNum = []		# List containing the numbers corresponding to the answers
			for y in outer_key:
				number = controller.get_answer_results(course, x, y)
				ansNum.append(number)
			bank[question_text] = outer_key, ansNum
		return bank

	def get_SA_responses(self, course):
		questions = controller.search_surveyID(course) #Returns a tuple of text questions
		ID = []
		for question in questions: # Returns a list of question ID number
			ID.append(controller.search_questionID(question))
		SAQuestions = controller.get_ID_MC_SA(ID, 'SA')
		print(SAQuestions)

		# Now we get the answers associated with the question:
		results = {}
		for x in SAQuestions:
			sa_answer = controller.get_SA_responses(course, x)
			question_text = controller.find_question(x)
			results[question_text] = sa_answer
		return results

	def get_course_list(self):
		course_list = []
		f = open(self.course_filename)
		reader = csv.reader(f)
		for row in reader:
			course_list = course_list + [" ".join(row)]
		return course_list

	def get_status_of_course(self, course_name):
		result = controller.get_survey_status(course_name)
		return result

class Student():
	def __init__ (self, ID):
		self.ID = ID

	def submit_answers(self, course_name, question, answer_picked):
		questionID = controller.search_questionID(question)
		controller.add_to_answer_database(course_name, questionID, answer_picked)

	def get_courses(self):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		rows = cur.execute("SELECT course_name FROM student_enrolments WHERE id = ?", (self.ID,))
		student_courses = []
		for row in rows:
			student_courses = student_courses + list(row)
		con.close()
		return student_courses

	def get_semester(self):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		cur.execute("SELECT semester FROM student_enrolments WHERE id = ?", (self.ID,))
		semester = cur.fetchone()
		con.close()
		return semester[0]

	def survey_completed(self, course_name):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		cur.execute("UPDATE student_enrolments SET survey_completed = 'yes' WHERE id = ? AND course_name = ?", (self.ID, course_name))
		con.commit()
		con.close()

	def check_if_survey_completed(self, course_name):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()

		cur.execute("SELECT survey_completed FROM student_enrolments WHERE id = ? AND course_name = ?", (self.ID, course_name))
		result = cur.fetchone()
		con.close()
		return result[0]

	def view_answers(self, question_to_see):
		question_id = controller.search_questionID(question_to_see)
		answer_list = controller.search_answerText(question_id)
		return answer_list

class Staff():
	def __init__(self, ID):
		self.ID = ID

	def add_question_to_course(self, question, course_name):
		#First find id of the question_to_add
		question_id = controller.search_questionID(question)
		controller.add_to_survey(course_name, question_id)

	def delete_question_from_course(self, question, course_name):
		question_id = controller.search_questionID(question)
		controller.delete_question_from_survey(question_id, course_name)

	def check_for_duplicates(self, selected_course, selected_question):
		result = controller.check_for_duplicate(selected_course, selected_question)
		if result: # If question already exists
			return 1
		else:
			return 0

	# Gets the pool of questions
	def view_questions(self):
		questions = controller.view_all_questions()
		return questions

	def view_answers(self, question_to_see):
		question_id = controller.search_questionID(question_to_see)
		answer_list = controller.search_answerText(question_id)
		return answer_list

	def get_course_status(self, course_name):
		result = controller.get_survey_status(course_name)
		return result

	def list_of_courses_status(self, status):
		courses = controller.list_of_courses_status(status)
		return courses

class Admin(Staff):
	def __init__(self, ID):
		Staff.__init__(self, ID)

	def add_question(self, question, questionType, answers):
		questionID = random.randint(1,1000)
		answerID = questionID
		controller.add_questionText(questionID, question, questionType)
		for answer in answers:
			controller.add_answerText(answerID, questionID, answer)

	def delete_question(self, question):
		question_id = controller.search_questionID(question)
		controller.delete_question(question_id)

	def change_survey_status(self, course_name, status):
		controller.change_survey_status(course_name, status)

	def get_survey_availabilities(self):
		survey_open = controller.count_survey_status('open')
		survey_close = controller.count_survey_status('close')
		survey_null = controller.count_survey_status('null')
		availability = [survey_open, survey_close, survey_null]
		return availability

class Teacher(Staff):
	def __init__(self, ID):
		Staff.__init__(self, ID)

	def pass_review(self, course_name):
		controller.change_survey_status(course_name, 'open')

	def get_surveys_to_review(self):
		con = sqlite3.connect("survey_database.db")
		cur = con.cursor()
		rows = cur.execute("SELECT course_name FROM survey_availability WHERE availability = 'review'")
		courses = []
		for row in rows:
			courses = courses + list(row)
		con.close()
		return courses

admin = Teacher('50')
print(admin.view_questions())
