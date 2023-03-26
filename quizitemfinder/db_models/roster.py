from ..io import get_roster, has_roster, save_roster, get_semesters, get_courses, DATA_PATH
import re
from io import StringIO
import csv
def validate_username(username):
    return not not re.match(r"^\w+$", username)
def validate_semester(semester):
    return not re.search(r"[<>%\$^?.!*]", semester)
def validate_course(course):
    print(course)
    print(re.search(r"[<>%\$^?.!*]", course))
    print(not re.search(r"[<>%\$^?.!*]", course))
    return not re.search(r"[<>%\$^?.!*]", course)

class Roster():
    def __init__(self, username, semester, course):
        if(not validate_username(username)):
            raise TypeError('username not valid')
        if(not validate_semester(semester)):
            raise TypeError('semester not valid')
        if(not validate_course(course)):
            print(course)
            raise Exception('coursename not valid')
        self.username = username
        self.semester = semester
        self.course = course

    def set_roster(self, csv_string):
        roster_file = StringIO(csv_string)
        roster_data = list(csv.reader(roster_file))
        save_roster(self.username, self.semester, self.course, roster_data, data_path=DATA_PATH)

    def get_roster(self):
        return get_roster(self.username, self.semester, self.course, data_path=DATA_PATH)

    def exists(self):
        return has_roster(self.username, self.semester, self.course, data_path=DATA_PATH)

    @staticmethod
    def all_semesters(username):
        return get_semesters(username, data_path=DATA_PATH)

    @staticmethod
    def all_courses(username, semester):
        return get_courses(username, semester, data_path=DATA_PATH)
