# Checking how the courses.csv is written
import csv

course_list = []
with open('courses.csv', 'r') as course_file:
	reader = csv.reader(course_file)
	course_file = list(reader)
	del course_file[0]
	for course in course_file:
		new_course = new_course + course
	print(new_course)