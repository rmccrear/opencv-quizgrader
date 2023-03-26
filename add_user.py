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
    roster = """ID,NAME,EMAIL
10001,Roger,stu1@myschool.edu
1002,Jenny,stu2@myschool.edu
1003,John,stu2@myschool.edu
1004,Dovie ,*
1005,Daniel,*
1006,Rossana  ,*
1007,Gretchen  ,*
1008,Margery  ,*
1009,Keva  ,*
1010,Elliot ,* 
1011,Shay  ,*
1012,Eleanor ,* 
1013,Dorthea  ,*
1014,Elvie  ,*
1015,Gerard  ,*
1016,Cassie  ,*
1017,Lula  ,*
1018,Lady  ,*
1019,Walter  ,*
1020,Delores  ,*
1021,Stanley  ,*
1022,Cheree  ,*
1023,Jefferson ,* 
1024,Janis  ,*
1025,Ressie  ,*
1026,Gretta  ,*
1027,Noah  ,*
1028,Chanelle,*  
1029,Nguyet  ,*
1030,Sharmaine ,* 
1031,Cecila  ,*
1032,Stacia  ,*
1033,Latia  ,*
1034,Carry  ,*
1035,Carmelo  ,*
1036,Franklin  ,*
1037,Riley  ,*
1038,Lesha  ,*
1039,Lauran  ,*
1040,Yoshie  ,*
1041,Mitsue  ,*
1042,Wilda  ,*
1043,Elisha  ,*
1044,Carisa  ,*
1045,Camellia  ,*
1046,Jeanie  ,*
1047,Kathryn  ,*
1048,Loura  ,*
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
