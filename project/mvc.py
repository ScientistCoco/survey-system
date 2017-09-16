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
        # by returning the questionID
        all_questions = model.search_surveyID(course_name)
        return view.view_survey_questions(all_questions)
        pass

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

    def add_questionText(self, questionID, questionText):
        model = SurveyModel()
        model.add_questionText(questionID, questionText)

    def add_answerText(self, answerID, questionID, answerText):
        model = SurveyModel()
        model.add_answerText(answerID, questionID, answerText)

    def delete_question(self, questionID):
        model = SurveyModel()
        model.delete_question(questionID)

    def delete_question_from_survey(self, questionID, course_name):
        model = SurveyModel()
        model.delete_question_from_survey(questionID, course_name)
# Model
class SurveyModel(object):
    def search_surveyID(self, course_name):
        query = "SELECT questionID from survey where course_name = '%s'" %course_name
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

    def add_questionText(self, questionID, questionText):
        query = "INSERT INTO question VALUES ('%s', '%s')" %(questionID, questionText)
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
        return all_questions
# Testing bitss
#print(controller.search_surveyID('COMP1521'))
#controller.add_to_survey('COMP1521', '28')
#print(controller.search_surveyID('COMP1521'))
