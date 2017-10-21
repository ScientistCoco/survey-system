import pytest
import unittest
import os
import random, string
from classes import Staff, Admin, Survey_system, Database, Teacher

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

class Create_Survey(unittest.TestCase):
    def test_add_question_to_course(self): # User story 5
        admin = Admin('50')
        survey = Survey_system('courses.csv', admin)
        questions = admin.view_questions()
        admin.add_question_to_course(questions[0], 'SENG2011 17s2')
        # Check that question has been added

        # Check that there are no duplicate questions
        course_questions = survey.get_question('SENG2011 17s2')
        duplicate_count = course_questions.count(questions[0])
        assert duplicate_count == 1

    def test_add_questions(self): #User Story 5
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

class ChangeCourseStatus(unittest.TestCase):    #User Story 6
# As the admin I should be able to change the current status of a course survey
# so I can manage who can view the survey
    def test_change_status_open(self):
        admin = Admin('admin')
        # Change the status to open
        admin.change_survey_status('SENG2011 17s2', 'close')
        status = admin.get_course_status('SENG2011 17s2')
        assert(status == 'open')

    def test_change_status_close(self):
        admin = Admin('admin')
        admin.change_survey_status('SENG2011 17s2', 'open')
        assert(admin.get_course_status('SENG2011 17s2') == 'close')

    def test_change_status_review(self):
        admin = Admin('admin')
        admin.change_survey_status('SENG2011 17s2', 'review')
        assert(admin.get_course_status('SENG2011 17s2') == 'review')

class CoursePassReview(unittest.TestCase):  # User Story 7
# As a teacher I should be able to see which course surveys I need to review so
# that I can check that it is okay before publishing it for student answers
    def test_pass_review(self):
        # First put the course into review
        admin = Admin('admin')
        admin.change_survey_status('SENG2011 17s2', 'review')

        # Now the teacher should be able to pass the course survey
        teacher = Teacher('50')
        teacher.pass_review('SENG2011 17s2')
        assert(admin.get_course_status('SENG2011 17s2') == 'open')

if __name__=="__main__":
    unittest.main()
