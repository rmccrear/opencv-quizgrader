import jwt
import bcrypt

key = b'secret pass word'

def get_username_from_jwt(token):
    decoded = jwt.decode(token, key, algorithms='HS256')
    return decoded['username']

def auth_user_from_password(username, passwd):
    user = find_user_in_password_file(username)
    if(user is not None):
       hashed_pw = user['hashed_pw'].encode('utf-8')
       input_pw = passwd.encode('utf-8')
       hashed_input = bcrypt.hashpw(input_pw, hashed_pw) 
       if(hashed_pw == hashed_input):
           return True
    return False

def gen_jwt_for_user(username, passwd):
    if(auth_user_from_password(username, passwd)):
        encoded_jwt = jwt.encode({'username': username}, key, algorithm='HS256')
        return encoded_jwt
    else:
        return False

def find_user_in_password_file(username):
    with open('./users/users') as f:
        lines = f.read().splitlines()
        user = None
        line = None 
        while(len(lines)>0 and user is None):
            line = lines.pop()
            u = line.split(':')
            if(u[0] == username):
               user = u 
               return {
                       'username': u[0],
                       'hashed_pw': u[1]
                      }
    return None

def check_user_exists(username):
    user = find_user_in_password_file(username)
    if(user is not None):
        return True
    else:
        return False

# from flask import Flask
#from flask import render_template
from flask import request
from flask import make_response

def setup_auth(app):
    @app.route("/users/login", methods=['GET', 'POST'])
    def login_user():
        if request.method == 'GET':
            return """ 
                    <form method="POST">
                        <p>username: <input type="text" name="username" placeholder="username">
                        <p>password: <input type="password" name="passwd">
                        <p><input type="submit" value="Login">
                    </form>
            """
        if request.method == 'POST':
            username = request.form['username']
            passwd   = request.form['passwd']
            jwt_token = gen_jwt_for_user(username, passwd)
            html =  """
                <p> welcome {username} </p>
                <script>
                    window.localStorage.setItem('quizgrader_auth_token', '{jwt_token}');
                </script>
                <p> <a href="/quizzes/{username}">Go to your quizzes </a> </p>
            """.format(username=username, jwt_token=jwt_token.decode("utf-8"))
            resp = make_response(html)
            resp.set_cookie('quizgrader_auth_token', jwt_token)
            return resp

def login_from_cookie(request):
    token = request.cookies.get('quizgrader_auth_token')
    try:
        username = get_username_from_jwt(token.encode('utf-8'))
        return username
    except Exception as e:
        return None

def login_from_header(request):
    token = request.headers.get('Authorization')
    try:
        username = get_username_from_jwt(token.encode('utf-8'))
        return username
    finally:
        return None
