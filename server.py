from flask import Flask
from flask import send_file
from flask import render_template
from flask import request, Response, redirect
import csv
import json
import urllib
import glob
import os


app = Flask(__name__)
#app.config['SECRET_KEY'] = '12345'
#app.config['LOCAL'] = 'TRUE'
app.config['LOCAL'] = os.environ.get('LOCAL', 'TRUE')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '12345')

if(app.config['SECRET_KEY'] == '12345'):
	print("WARNING: PLEASE SET SECRET_KEY environ variable!")


from quizitemfinder.io import create_quiz_directory_structure, header_im_path, count_headers, count_sheets, get_roster, set_student_ids_for_quiz, get_student_ids_for_quiz, set_scores_for_quiz, get_scores_for_quiz, get_answer_key, save_answer_key, get_corrections, error_sheet_path, error_corrected_sheet_path, get_sheets_with_errors, find_sheet_dims, is_quiz_finished, set_score_for_items
from quizitemfinder.process_quiz import do_process_quiz
from quizitemfinder.process_graded_sheets import save_graded_sheets_for_quiz, convert_graded_to_pdf

import auth
from flask_login import LoginManager, login_required

login_manager = LoginManager()
login_manager.init_app(app)



secret_key = app.config['SECRET_KEY'] 
auth.setup_auth(app, login_manager, secret_key)

from app.splash import setup_splash
# from app.users import setup_users
from app.process_scanned_pdf import setup_process_scanned_pdf
from app.exporting import setup_exporting
from app.answer_key import setup_answer_key
from app.scoring import setup_scoring

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

setup_splash(app)


# setup_users(app)


@app.route("/quizzes/<username>/")
@login_required
def user_quizzes(username):
    quizzes = glob.glob('./score_data/' + username + "/processed_quizzes/*/")
    qs = [os.path.basename(os.path.normpath(q)) for q in quizzes]
    qs.sort()
    finished_hash = {}
    for q in qs:
        finished_hash[q] = is_quiz_finished(username, q)
    return render_template("quiz_list.html", quizzes=qs, username=username, finished_hash=finished_hash)


setup_process_scanned_pdf(app)

setup_exporting(app)

setup_answer_key(app)

setup_scoring(app)


