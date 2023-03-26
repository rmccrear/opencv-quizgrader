import jwt
import bcrypt






# from flask import Flask
#from flask import render_template
from flask import request, redirect, url_for, flash, render_template
from flask import make_response
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

class User(UserMixin):
    def __init__(self):
        self.id = None
    def set_id(self, id):
        self.id = id
    def get_id(self):
        return self.id


import glob
import os




def setup_auth(app, login_manager, secret_key):

    key = secret_key

    ## MARK: user file
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


    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect(url_for('login_user_route'))


    # @login_manager.request_loader
    # def load_user_from_request(request):
    #    api_key = request.headers.get('Authorization')
    #    return None
    @login_manager.user_loader
    def user_loader(user_id):
        user = User()
        user.set_id(user_id)
        return user

    if(app.config['LOCAL'] == 'TRUE'):
        @app.route("/users/")
        def users():
            users = glob.glob('./score_data/*'   )
            us = [os.path.basename(u) for u in users]
            # user_links = ["<a href='/quizzes/{0}/'> {0} </a>".format(u) for u in us]
            user_links = ["<a href='{0}'> {1} </a>".format(url_for('login_username', username=u), u) for u in us]
            user_li = [ "<li style='font-size: xx-large;'> {0} </li>".format(a) for a in  user_links]
            return " ".join(user_li) 
    
        @app.route("/users/login_user/<username>")
        def login_username(username):
            user = User()
            user.set_id(username)
            login_user(user)
            flash('Logged in successfully.')
            # return flask.redirect(next or flask.url_for('index'))
            return redirect(url_for('user_quizzes', username=username))


    @app.route("/users/logout_user")
    def logout_user_route():
        #user = User()
        #user.set_id(username)
        logout_user()
        flash('Logged out successfully.')
        # return flask.redirect(next or flask.url_for('index'))
        return redirect(url_for('splash_page'))


    @app.route("/users/am_i_logged_in", methods=['GET', 'POST'])
    @login_required
    def amiloggedin():
        return "yes, {}".format(current_user.id)


    @app.route("/users/login/", methods=['GET', 'POST'])
    def login_user_route():
        if request.method == 'GET':
            return render_template("login.html")

        if request.method == 'POST':
            username = request.form['username']
            passwd   = request.form['passwd']
            if(auth_user_from_password(username, passwd)):
                user = User()
                user.set_id(username)
                login_user(user, remember=True)

            jwt_token = gen_jwt_for_user(username, passwd)
            html =  """
                <p> welcome {username} </p>
                <script>
                    window.localStorage.setItem('quizgrader_auth_token', '{jwt_token}');
                </script>
                <p> <a href="{quiz_url}">Go to your quizzes </a> </p>
            """.format(quiz_url=url_for('user_quizzes', username=username), username=username, jwt_token=jwt_token.decode("utf-8"))
            resp = make_response(html)
            resp.set_cookie('quizgrader_auth_token', jwt_token)
            return resp

    @app.route("/users/register", methods=['GET', 'POST'])
    def register_user_route():
        if request.method == 'GET':
            return render_template("login_register.html")
        if request.method == 'POST':
            email = request.form['email']
            save_email_registration(email)
            return render_template("login_thank_you_for_registering.html")

def save_email_registration(email):
    from datetime import datetime
    from time import time
    ts = time()
    date_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    with open("./registrations.txt", "a+") as f:
        f.write("{}\t{}\n".format(email, date_str))



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
