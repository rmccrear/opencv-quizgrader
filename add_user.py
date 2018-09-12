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
4,Dovie ,*
5,Daniel,*
6,Rossana  ,*
7,Gretchen  ,*
8,Margery  ,*
9,Keva  ,*
10,Elliot ,* 
11,Shay  ,*
12,Eleanor ,* 
13,Dorthea  ,*
14,Elvie  ,*
15,Gerard  ,*
16,Cassie  ,*
17,Lula  ,*
18,Lady  ,*
19,Walter  ,*
20,Delores  ,*
21,Stanley  ,*
22,Cheree  ,*
23,Jefferson ,* 
24,Janis  ,*
25,Ressie  ,*
26,Gretta  ,*
27,Noah  ,*
28,Chanelle,*  
29,Nguyet  ,*
30,Sharmaine ,* 
31,Cecila  ,*
32,Stacia  ,*
33,Latia  ,*
34,Carry  ,*
35,Carmelo  ,*
36,Franklin  ,*
37,Riley  ,*
38,Lesha  ,*
39,Lauran  ,*
40,Yoshie  ,*
41,Mitsue  ,*
42,Wilda  ,*
43,Elisha  ,*
44,Carisa  ,*
45,Camellia  ,*
46,Jeanie  ,*
47,Kathryn  ,*
48,Loura  ,*
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
