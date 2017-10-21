import pytest
import unittest
import os
import random, string
from classes import Staff, Admin, Survey_system, Database

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

class Create_Survey(unittest.TestCase):
    def test_add_question_to_course(self):
        admin = Admin('50')
        survey = Survey_system('courses.csv', admin)
        questions = admin.view_questions()
        admin.add_question_to_course(questions[0], 'SENG2011 17s2')
        # Check that question has been added

        # Check that there are no duplicate questions
        course_questions = survey.get_question('SENG2011 17s2')
        duplicate_count = course_questions.count(questions[0])
        assert duplicate_count == 1

    def test_add_questions(self):
        # Test adding questions without supplying MC answers and answer type
        admin = Admin('50')
        prev_list_question = admin.view_questions()
        string = randomword(10)

        admin.add_question(string)
        new_list = admin.view_questions()
        assert (len(prev_list_question) + 1) == (len(new_list)), "FAILED to add question"

    def test_create_mandatory_question(self):
        admin = Admin('admin')
        survey = Survey_system('courses.csv', admin)
        course_questions = survey.get_question('SENG2011 17s2')
        admin.push_mandatory_questions('SENG2011 17s2', [(course_questions[0])])
        # Check that the question is now mandatory in the database
        assert (admin.get_mandatory_status('SENG2011 17s2', course_questions[0])[0] == 'Yes')

class Enrolments(unittest.TestCase):
    def test_enrol_invalid_student(self):
        student = Database()
        student.enrol_student('50', 'SENG2011', '17s2')
        # Test for enrolling an invalid student
        assert (student.count_students('50', 'SENG2011', '17s2') == 0), "FAILED in test for enrolling an invalid student"

    def test_enrol_valid_student(self):
        student = Database()
        student.enrol_student('100', 'COMP9333', '17s2')

        assert(student.count_students('100', 'COMP9333', '17s2') == 1), "FAILED to enroll a student"

if __name__=="__main__":
    unittest.main()
