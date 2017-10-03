# MVC structure
import sqlite3
# Controller module
class Controller(object):
    def __init__(self):
        pass

    def search_surveyID(self, course_name):
        model = SurveyModel()
        view = SurveyView()
        # Return a list of all the questions in the course survey
        all_questions = model.search_surveyID(course_name)
        return view.view_survey_questions(all_questions)

    def add_to_survey(self, course_name, questionID):
        model = SurveyModel()
        model.add_to_survey(course_name, questionID)

    def view_all_questions(self):
        model = SurveyModel()
        view = SurveyView()
        all_questions = model.view_all_questions()
        return view.view_all_questions(all_questions)

    def search_questionID(self, questionID):
        model = SurveyModel()
        view = SurveyView()
        question = model.search_questionID(questionID)
        return view.view_questionID(question)

    def search_answerText(self, answerID):
        model = SurveyModel()
        view = SurveyView()
        answer = model.search_answerText(answerID)
        return view.view_answerID(answer)

    def add_questionText(self, questionID, questionText, questionType):
        model = SurveyModel()
        model.add_questionText(questionID, questionText, questionType)

    def add_answerText(self, answerID, questionID, answerText):
        model = SurveyModel()
        model.add_answerText(answerID, questionID, answerText)

    def delete_question(self, questionID):
        model = SurveyModel()
        model.delete_question(questionID)

    def delete_question_from_survey(self, questionID, course_name):
        model = SurveyModel()
        model.delete_question_from_survey(questionID, course_name)

    # Adds the survey responses to the survey_answer table
    def add_to_answer_database(self, course_name, questionID, answer_picked):
        model = SurveyModel()
        model.add_to_answer_database(course_name, questionID, answer_picked)

    # Find status of survey
    def get_survey_status(self, course_name):
        model = SurveyModel()
        status = model.get_survey_status(course_name)
        view = SurveyView()
        return view.view_survey_status(status)

    # Change the status of the survey
    def change_survey_status(self, course_name):
        model = SurveyModel()
        model.change_survey_status(course_name)
# Model
class SurveyModel(object):
    def search_surveyID(self, course_name):
        query = "SELECT questionID from survey where course_name = '%s'" %(course_name)
        questionID = self._dbselect(query)
        # Then make a list of all the questions
        question_list = []
        for id in questionID:
            question_list = question_list + list(self.find_question(id))
        return question_list

    def add_to_survey(self, course_name, questionID):
        query = "INSERT INTO survey VALUES ('%s', '%s')" %(course_name, questionID)
        self._dbinsert(query)

    def view_all_questions(self):
        query = "SELECT question_text from question"
        all_questions = self._dbselect(query)
        return all_questions

    # Returns the question corresponding to the id
    def find_question(self, questionID):
        query = "SELECT question_text from question where questionID = '%s'" %questionID
        question = self._dbselect(query)
        return question

    # Returns the id corresponding to the question
    def search_questionID(self, question_text):
        query = "SELECT questionID from question where question_text = '%s'" %(question_text)
        question = self._dbselect(query)
        return question

    def search_answerText(self, answerID):
        query = "SELECT answer_text FROM answer where answerID = '%s'" %answerID
        answer = self._dbselect(query)
        return answer

    def add_questionText(self, questionID, questionText, questionType):
        query = "INSERT INTO question VALUES ('%s', '%s', '%s')" %(questionID, questionText, questionType)
        self._dbinsert(query)

    def add_answerText(self, answerID, questionID, answerText):
        query = "INSERT INTO answer VALUES ('%s', '%s', '%s')" %(answerID, questionID, answerText)
        self._dbinsert(query)

    def delete_question(self, questionID):
        query = "DELETE FROM question WHERE questionID = '%s'" %questionID
        self._dbinsert(query)
        query = "DELETE FROM answer where answerID = '%s'" %questionID
        self._dbinsert(query)

    def delete_question_from_survey(self, questionID, course_name):
        query = "DELETE FROM survey WHERE (questionID = '%s' AND course_name = '%s')" %(questionID, course_name)
        self._dbinsert(query)

    def add_to_answer_database(self, course_name, questionID, answer_text):
        query = "INSERT INTO survey_answers VALUES ('%s', '%s', '%s')" %(course_name, questionID, answer_text)
        self._dbinsert(query)

    def get_survey_status(self, course_name):
        query = "SELECT availability from survey_availability WHERE course_name = '%s'" %course_name
        result = self._dbselect(query)
        # Check if the course exists if it doesn't then we return a closed value
        if not result:
            query = "INSERT INTO survey_availability VALUES ('%s', '%s')" %(course_name, 'close')
            self._dbinsert(query)
            result = ['close']
        return result

    def change_survey_status(self, course_name):
        # First get the status:
        result = self.get_survey_status(course_name)
        if result[0] == 'close':
            query = "UPDATE survey_availability SET availability = 'open' WHERE course_name = '%s'" %(course_name)
        else:
            query = "UPDATE survey_availability SET availability = 'close' WHERE course_name = '%s'" %(course_name)
        self._dbinsert(query)

    # For searching items in the database and returning the results
    def _dbselect(self, query):
        connection = sqlite3.connect('survey_database.db')
        cursorObj = connection.cursor()

        # Executing the query
        rows = cursorObj.execute(query)
        connection.commit()
        results = ()
        for row in rows:
            results = results + row
        cursorObj.close()
        return results

    def _dbinsert(self, query):
        connection = sqlite3.connect('survey_database.db')
        cursorObj = connection.cursor()

        # Executing the query
        rows = cursorObj.execute(query)
        connection.commit()
        cursorObj.close()

# View
class SurveyView(object):
    def view_questionID(self, questionID):
        #questionID in tupple format so we only want to get first item
        return questionID[0]

    def view_answerID(self, answerID):
        return answerID

    def view_all_questions(self, all_questions):
        question_list = []
        for question in all_questions:
            question_list.append(question)
        return question_list

    def view_survey_questions(self, all_questions):
        questions = []
        for question in all_questions:
            questions.append(question)
        return questions

    def view_survey_status(self, status):
        return status[0]
# Testing bitss
#controller = Controller()
#print(controller.search_surveyID('COMP1521'))
#controller.add_to_survey('COMP1521', '28')
#print(controller.search_surveyID('COMP1531'))
