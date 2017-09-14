# MVC structure
import sqlite3
# Controller module
class Controller(object):
    def __init__(self):
        pass

    def search_surveyID(self, surveyID):
        pass

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

# Model
class SurveyModel(object):
    def search_surveyID(self, surveyID):
        pass

    def view_all_questions(self):
        query = "SELECT question_text from question"
        all_questions = self._dbselect(query)
        return all_questions

    def search_questionID(self, question_text):
        query = "SELECT questionID from question where question_text = '%s'" %question_text
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

# Testing bitss
controller = Controller()
all_questions = controller.view_all_questions()
print(all_questions)
question_answer = {}
for question in all_questions:
    questionID = controller.search_questionID(question)
    print(questionID)
    question_answer[question] = controller.search_answerText(questionID)

print(question_answer)
