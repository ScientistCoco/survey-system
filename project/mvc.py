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


    def find_question(self, question):
        model = SurveyModel()
        result = model.find_question(question)
        if result:
            return result[0]

    # Returns the question corresponding to the id
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
    def change_survey_status(self, course_name, status):
        model = SurveyModel()
        model.change_survey_status(course_name, status)

    # Returns the number of courses with the status in question
    def count_survey_status(self, status):
        model = SurveyModel()
        result = model.count_survey_status(status)
        return result

    # Returns the list of courses with the status in question
    def list_of_courses_status(self, status):
        model = SurveyModel()
        result = model.list_of_courses_status(status)
        return result

    def get_ID_MC_SA(self, questionIDs, q_type):
        model = SurveyModel()
        result = model.get_ID_MC_SA(questionIDs, q_type)
        return result

    def check_for_duplicate(self, selected_course, selected_question):
        model = SurveyModel()
        result = model.check_for_duplicate(selected_course, selected_question)
        return result

    # Gets the number of responses
    def get_answer_results(self, course_name, questionID, answerText):
        model = SurveyModel()
        result = model.get_answer_results(course_name, questionID, answerText)
        return result

    # Get a list of the SA responses
    def get_SA_responses(self, course_name, questionID):
        model = SurveyModel()
        result = model.get_SA_responses(course_name, questionID)
        return result

    def push_mandatory_questions(self, questions, course_name):
        model = SurveyModel()
        model.push_mandatory_questions(questions, course_name)

    def get_mandatory_status(self, course_name, question):
        model = SurveyModel()
        result = model.get_mandatory_status(course_name, question)
        return result

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
        query = "INSERT INTO survey (course_name, questionID) VALUES ('%s', '%s')" %(course_name, questionID)
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
        print(result)
        # Check if the course exists if it doesn't then we return a closed value
        #if not result:
        #    query = "INSERT INTO survey_availability VALUES ('%s', '%s')" %(course_name, 'close')
        #    self._dbinsert(query)
        #    result = ['close']
        return result

    def change_survey_status(self, course_name, status):
        if status == 'review':
            query = "UPDATE survey_availability SET availability = 'review' WHERE course_name = '%s'" %(course_name)
        else:
            # First get the status:
            result = self.get_survey_status(course_name)
            if result[0] == 'close' or result[0] == 'review':
                query = "UPDATE survey_availability SET availability = 'open' WHERE course_name = '%s'" %(course_name)
            else:
                query = "UPDATE survey_availability SET availability = 'close' WHERE course_name = '%s'" %(course_name)
        self._dbinsert(query)

    def count_survey_status(self, status):
        if status == 'null':
            query = "SELECT count(*) FROM survey_availability WHERE availability IS NULL"
        else:
            query = "SELECT count(*) FROM survey_availability WHERE availability = '%s'" %(status)
        result = self._dbselect(query)
        return result[0]

    def list_of_courses_status(self, status):
        query = "SELECT course_name FROM survey_availability WHERE availability = '%s'" %(status)
        result = self._dbselect(query)
        return result

    def get_ID_MC_SA(self, questionIDs, q_type):
        # Find the questiosn that are MC
        IDs = []
        for questionID in questionIDs:
            query = "SELECT questionID FROM question WHERE (question_type = '%s' AND questionID = '%s')" %(q_type, questionID)
            result = self._dbselect(query)
            if result:
                IDs.append(result[0])
        # Now find the questions that are MC
        return IDs

    def check_for_duplicate(self, selected_course, selected_question):
        ID = (self.search_questionID(selected_question))[0]
        #print(ID)
        query = "SELECT * FROM survey WHERE (course_name = '%s' AND questionID = '%s')" %(selected_course, ID)
        result = self._dbselect(query)
        return result

    def get_answer_results(self, course_name, questionID, answerText):
        query = "SELECT COUNT(*) FROM survey_answers WHERE (course_name = '%s' AND questionID = '%s' AND answer_text = '%s')" %(course_name, questionID, answerText)
        result = self._dbselect(query)
        return result[0]

    def get_SA_responses(self, course_name, questionID):
        query = "SELECT answer_text FROM survey_answers WHERE (course_name = '%s' AND questionID = '%s')" %(course_name, questionID)
        result = self._dbselect(query)
        return result

    def push_mandatory_questions(self, qID, course_name):
        query = "UPDATE survey SET requisitness = 'Yes' where questionID = '%s' AND course_name = '%s'" %(qID, course_name)
        self._dbinsert(query)

    def get_mandatory_status(self, course_name, question):
        query = "SELECT requisitness FROM survey where (course_name = '%s' AND questionID = '%s')" %(course_name, question)
        result = self._dbselect(query)
        return result

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
        if questionID:
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
