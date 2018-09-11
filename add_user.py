import getpass
import os
import bcrypt
import sys

from quizitemfinder.io import ensure_dir

username = input('username to add: ')

try:
    os.makedirs("./score_data/{}/my_courses/106-2/ENG-101".format(username))   # examples
except:
    print('user already exists')
    sys.exit(1)

try:
    os.makedirs("./users")
except:
    pass


# example
with open("./score_data/{}/my_courses/106-2/ENG-101/roster.csv".format(username), "w+") as myfile:
    roster = """10001,Roger,stu1@myschool.edu
10002,Jenny,stu2@myschool.edu
10003,John,stu2@myschool.edu
"""
    myfile.write(roster)

#if( not os.path.isfile("./users/users") ):
#    ensure_dir("./users")
#    open("./users/users", "w+")



password = getpass.getpass('password for user: ').encode('utf-8')
password_hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8", "strict") 
user_line = "{}:{}\n".format(username, password_hashed)

with open("./users/users", "a+") as myfile:
    myfile.write(user_line)


print("\n put a file called 'roster.csv' into ./score_data/{}/my_courses/106-2/ENG-101 to set up your class.\n".format(username))
