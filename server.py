from flask import Flask
from flask import send_file
from flask import render_template
from flask import request, Response, redirect
import csv
import json
import urllib
app = Flask(__name__)

import glob
import os


from quizitemfinder.io import create_quiz_directory_structure, header_im_path, count_headers, count_sheets, get_roster, set_student_ids_for_quiz, get_student_ids_for_quiz, set_scores_for_quiz, get_scores_for_quiz, get_answer_key, save_answer_key, get_corrections, error_sheet_path, error_corrected_sheet_path, get_sheets_with_errors, find_sheet_dims
from quizitemfinder.process_quiz import do_process_quiz
from quizitemfinder.process_graded_sheets import save_graded_sheets_for_quiz, convert_graded_to_pdf

import auth

auth.setup_auth(app)

@app.route("/")
def hello():
    return render_template("splash.html")

@app.route("/users/")
def users():
    users = glob.glob('./score_data/*'   )
    us = [os.path.basename(u) for u in users]
    user_links = ["<a href='/quizzes/{0}/'> {0} </a>".format(u) for u in us]
    user_li = [ "<li style='font-size: xx-large;'> {0} </li>".format(a) for a in  user_links]
    return " ".join(user_li) 

@app.route("/quizzes/<username>/")
def user_quizzes(username):
    quizzes = glob.glob('./score_data/' + username + "/processed_quizzes/*")
    qs = [os.path.basename(q) for q in quizzes]
    return render_template("quiz_list.html", quizzes=qs, username=username)


@app.route("/new-quiz/<username>/", methods=['GET', 'POST'])
def new_quiz(username):
    if request.method == 'GET':
        #return render_template("_quiz_form.html")
        return render_template("new_quiz.html", username=username)
    if request.method == 'POST':
        semester = request.form['semester'].replace(' ', '-');
        course_name = request.form['course_name'].replace(' ', '-');
        quiz_name = request.form['quiz_name'].replace(' ', '-');
        answer_key = request.form['answer_key'].split()
        full_quiz_name = "{}--{}--{}".format(semester, course_name, quiz_name)
        f = request.files['quiz_pdf']
        create_quiz_directory_structure(username, full_quiz_name)
        f.save('./score_data/{}/processed_quizzes/{}/{}.pdf'.format(username, full_quiz_name, full_quiz_name))
        results = do_process_quiz(username, full_quiz_name, answer_key)

        error_sheet_nos = results["errors"]
        return render_template("quiz_complete.html", 
                               error_sheet_nos=error_sheet_nos,
                               username=username,
                               quiz_name=full_quiz_name)
        #return "<p>FINISHED PROCESSING -- " + full_quiz_name +  "<p>errors: " + ", ".join([str(e) for e in results["errors"]]) + "<p> View your quiz: <a href='/quiz/{}/{}'> {} </a>".format(username, full_quiz_name, full_quiz_name)


@app.route("/reprocess-quiz/<username>/<full_quiz_name>", methods=['GET'])
def reprocess_quiz(username, full_quiz_name):
    create_quiz_directory_structure(username, full_quiz_name)
    saved_pdf = './score_data/{}/processed_quizzes/{}/{}.pdf'.format(username, full_quiz_name, full_quiz_name)
    results = do_process_quiz(username, full_quiz_name, [])
    error_sheet_nos = results["errors"]
    return render_template("quiz_complete.html", 
                               error_sheet_nos=error_sheet_nos,
                               username=username,
                               quiz_name=full_quiz_name)
    #return "<p>POSTED -- " + full_quiz_name +  "<p>errors: " + ", ".join([str(e) for e in results["errors"]]) + "<p> <a href='/quiz/{}/{}'> {} </a>".format(username, full_quiz_name, full_quiz_name)
    
@app.route("/quiz-errors/<username>/<quiz_name>", methods=['GET'])
def view_quiz_errors(username, quiz_name):
    error_sheet_nos = get_sheets_with_errors(username, quiz_name)
    return render_template("quiz_complete.html", 
                               error_sheet_nos=error_sheet_nos,
                               username=username,
                               quiz_name=quiz_name)

    
@app.route("/quiz-scores/<username>/<quiz_name>.csv")
def quiz_scores(username, quiz_name):
    set_scores_for_quiz(username, quiz_name)
    score_rows = get_scores_for_quiz(username, quiz_name)
    score_str = "\n".join([",".join(row) for row in score_rows])
    # csv_path = 'score_data/{}/processed_quizzes/{}/scoring/corrections.csv'.format(username, quiz_name)
    return Response(score_str, mimetype='text/csv')
    # return send_file(csv_path, mimetype='text/csv') 


import time
from quizitemfinder.process_pdf import export_sheets_with_student_numbers
@app.route("/finish-quiz/<username>/<quiz_name>")
def finish_graded_quiz(username, quiz_name):
    t1 = time.perf_counter() 
    set_scores_for_quiz(username, quiz_name)
    t2 = time.perf_counter() 
    app.logger.info('set_scores done in {} sec'.format(float(t2-t1)))

    t1 = time.perf_counter() 
    save_graded_sheets_for_quiz(username, quiz_name)
    t2 = time.perf_counter() 
    app.logger.info('save graded sheets done in {} sec'.format(float(t2-t1)))
    export_sheets_with_student_numbers(username, quiz_name)

    t1 = time.perf_counter() 
    convert_graded_to_pdf(username, quiz_name)
    t2 = time.perf_counter() 
    app.logger.info('convert graded sheets done in {} sec'.format(float(t2-t1)))

    return redirect('/quiz/{}/{}'.format(username, quiz_name))
    #overlay_url = "/finished-quiz/overlay/{}/{}/{}--overlay.pdf".format(username, quiz_name, quiz_name)
    #graded_url = "/finished-quiz/graded/{}/{}/{}--graded.pdf".format(username, quiz_name, quiz_name)
    #return "<p> graded " + "<p><a href='{}'> overlay </a>".format(overlay_url) + "<p><a href='{}'> graded </a>".format(graded_url) 

@app.route("/finished-quiz/<grade_format>/<username>/<quiz_name>/<file_name>")
def send_graded_quiz(grade_format, username, quiz_name, file_name):
    graded_base_path = "score_data/{0}/processed_quizzes/{1}/sheets-graded".format(username, quiz_name)
    overlay_path = "{}/graded-overlays/graded-overlays.pdf".format(graded_base_path)
    reversed_overlay_path = "{}/graded-overlays/graded-overlays-reversed.pdf".format(graded_base_path)
    graded_sheet_path = "{}/graded-sheets/graded-sheets.pdf".format(graded_base_path)
    try:
        if(grade_format == 'overlay'):
            return send_file(overlay_path, mimetype='application/pdf') 
        if(grade_format == 'reversed-overlay'):
            return send_file(reversed_overlay_path, mimetype='application/pdf') 
        if(grade_format == 'graded'):
            return send_file(graded_sheet_path, mimetype='application/pdf') 
    except:
        return "<h1>Please Submit quiz for grading first. (Click the submit quiz button.)</h1>"
    
@app.route("/quiz/<username>/<quiz_name>")
def present_quiz(username, quiz_name):
    #auth_username = auth.login_from_cookie(request)
    #if(auth_username != username):
    #    return 'please login'
    answer_key = get_answer_key(username, quiz_name)
    answers = sorted(list(set(answer_key)))
    item_count = get_item_count(username, quiz_name)
    item_nos = range(item_count)
    semester = 'semester'; course_name='course'
    if(len(quiz_name.split('--')) > 2):
        semester = quiz_name.split('--')[0]
        course_name =  quiz_name.split('--')[1]
    return render_template("present_quiz.html", answers=answers, username=username, quiz_name=quiz_name, item_nos=item_nos, course_name=course_name, semester=semester)

    
@app.route("/quiz-answer-key/<username>/<quiz_name>", methods=['GET', 'POST'] )
def quiz_answer_key(username, quiz_name):
    sheet_no = 1 # answer key
    item_count = get_item_count(username, quiz_name)
    answer_key = get_answer_key(username, quiz_name)
    items = []

    if request.method == 'POST':
        answer_key = []
        for item_no in range(item_count):
            key_name = "answer_" + str(item_no)
            val = request.form.get(key_name, False)
            answer_key.append(val if val else '')
        save_answer_key(username, quiz_name, answer_key)

    for item_no in range(item_count): 
        ans = answer_key[item_no] if item_no < len(answer_key) else ''
        items.append( {'src': "/item-img/{}/{}/{}/{}".format(username, quiz_name, sheet_no, item_no),
                 'sheet_no': sheet_no,
                 'item_no': item_no,
                 'username': username,
                 'quiz_name': quiz_name,
                 'value': ans
            } )
    return render_template("answer_key.html", username=username, quiz_name=quiz_name, items=items, item_count=len(items))

@app.route("/quiz/<username>/<quiz_name>/<sheet_no>")
def user_quiz(username, quiz_name, sheet_no):
    img_src = "/sheet-img/{0}/{1}/{2}.jpeg".format(username, quiz_name, sheet_no)
    return "<img src={}>".format(img_src)

@app.route("/sheet-img/<username>/<quiz_name>/<sheet_no>.jpeg")
def serve_sheet_img(username, quiz_name, sheet_no):
    filename = "score_data/{0}/processed_quizzes/{1}/sheets/img-{2}.jpeg".format(username, quiz_name, sheet_no)
    return send_file(filename, mimetype='image/jpeg') 

@app.route("/error-img/<username>/<quiz_name>/<sheet_no>.png")
def serve_error_img(username, quiz_name, sheet_no):
    filename = "score_data/{0}/processed_quizzes/{1}/sheets/img-{2}.jpeg".format(username, quiz_name, sheet_no)
    filename = error_sheet_path(username, quiz_name, sheet_no)
    return send_file(filename, mimetype='image/jpeg') 

@app.route("/error-corrected-img/<username>/<quiz_name>/<sheet_no>.png")
def serve_error_corrected_img(username, quiz_name, sheet_no):
    filename = "score_data/{0}/processed_quizzes/{1}/sheets/img-{2}.jpeg".format(username, quiz_name, sheet_no)
    filename = error_corrected_sheet_path(username, quiz_name, sheet_no)
    return send_file(filename, mimetype='image/jpeg') 

@app.route("/item-img/<username>/<quiz_name>/<sheet_no>/<item_no>")
def serve_item_img(username, quiz_name, sheet_no, item_no):
    filename = "score_data/{0}/processed_quizzes/{1}/trimmed_img/l.{2}.i.{3}.png".format(username, quiz_name, sheet_no, item_no)
    return send_file(filename, mimetype='image/png') 

@app.route("/header-img/<username>/<quiz_name>/<sheet_no>/<header_no>")
def serve_header_img(username, quiz_name, sheet_no, header_no):
    filename = header_im_path(username, quiz_name, header_no, sheet_no) #"score_data/{0}/processed_quizzes/{1}/trimmed_img/l.{2}.i.{3}.png".format(username, quiz_name, sheet_no, item_no)
    return send_file(filename, mimetype='image/png') 

# MARK: headers and students
@app.route("/quiz-headers/<username>/<quiz_name>/<semester>/<course>")
def quiz_to_students(username, quiz_name, semester, course):
    roster = ''
    try:
        roster = get_roster(username, semester, course)
    except:
        return './score_data/{}/my_courses/{}/{}/roster.csv not found, please create it.'.format(username, semester, course)
    json_roster = json.dumps(roster)
    header_count = count_headers(username, quiz_name)
    sheet_count = count_sheets(username, quiz_name)
    quiz_headers = []
    for sheet_no in range(sheet_count) :
        headers = {
                  "sheet_no": sheet_no,
                  "imgs": [],
                  "data": [],
                  "length": 0
                }
        for header_no in range(header_count):
            headers["imgs"].append({
                    "img_src": "/header-img/{username}/{quiz_name}/{sheet_no}/{header_no}".format(username=username, quiz_name=quiz_name, sheet_no=sheet_no, header_no=header_no)
                        })
            headers["data"].append('')
            headers["length"] += 1
        quiz_headers.append(headers)

    sheet_no2student_id = get_student_ids_for_quiz(username, quiz_name)
    if(len(sheet_no2student_id ) < 1):
        app.logger.error('no studdnt ids in place yet')
        sheet_no2student_id = ['',''] + [s['student_id'] for s in roster]
    # sheet_no2student_id = get_sheets2student_ids(username, quiz_name)
    #if(len(sheet_no2student_id) < 1)):
    #    sheet_no2student_id = [s['student_id'] for s in s roster]
    return render_template("quiz_to_students.html", username=username, quiz_name=quiz_name, quiz_headers=quiz_headers, json_roster=json_roster, sheet_no2student_id=json.dumps(sheet_no2student_id))

@app.route("/save-students-for-quiz/<username>/<quiz_name>", methods=['POST'])
def save_quiz_to_students(username, quiz_name):
    data = request.get_json()
    set_student_ids_for_quiz(username, quiz_name, data)
    return json.dumps(data)


## throw out first two cols (col1 = student_id, col2 = average for this item)
CORR_LEFT_OFFSET = 2
# CORR_LEFT_OFFSET = 0
# MARK: corrections
@app.route("/corrections/set/<username>/<quiz_name>/<int:sheet_no>/<int:item_no>/<value>")
def set_correction(username, quiz_name, sheet_no, item_no, value):
    # open cvs
    # cvs[item_no] = value
    # save cvs
    filename = "score_data/{0}/processed_quizzes/{1}/scoring/corrections.csv".format(username, quiz_name)
    rows = []
    with open(filename, mode="r") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
        rows[sheet_no][item_no + CORR_LEFT_OFFSET] = value
    with open(filename, mode='w') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return value

@app.route("/corrections/get/<username>/<quiz_name>/<int:sheet_no>/<int:item_no>")
def get_correction(username, quiz_name, sheet_no, item_no):
    filename = "./score_data/{0}/processed_quizzes/{1}/scoring/corrections.csv".format(username, quiz_name)
    rows = []
    item_value = ''
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
        item_value = rows[sheet_no][item_no + CORR_LEFT_OFFSET]
    return item_value


@app.route("/items/<username>/<quiz_name>/<int:item_no>")
def serve_items(username, quiz_name, item_no):
    items = make_items(username, quiz_name, item_no)
    items_in_sheets = make_corrections(username, quiz_name)
    answer_value = ''
    try:
        answer_value = get_answer_key(username, quiz_name)[item_no]
    except:
        url = '/quiz-answer-key/{}/{}'.format(username, quiz_name)
        return 'Please go to set answer key first <a href="{}"> (go) </a>'.format(url)
    sheet_dims = find_sheet_dims(username, quiz_name, 0)

    return render_template("correct_items.html", items=items, items_in_sheets=items_in_sheets, answer_value=answer_value, sheet_dims=sheet_dims)

@app.route("/items-for-value/<username>/<quiz_name>/<path:answer_value>")
def serve_items_for_particular_answer(username, quiz_name,  answer_value):
    items = make_items_for_particular_answer(username, quiz_name,  answer_value)
    items_in_sheets = make_corrections(username, quiz_name)
    sheet_dims = find_sheet_dims(username, quiz_name, 0)
    return render_template("correct_items.html", items=items, items_in_sheets=items_in_sheets, answer_value=answer_value, username=username, quiz_name=quiz_name, sheet_dims=sheet_dims)

def make_items_for_particular_answer(username, quiz_name,  answer):
    indeces = get_indeces_for_value(username, quiz_name, answer)
    items = []
    for item_no in indeces:
        more_items = make_items(username, quiz_name, item_no)
        items.extend(more_items)
    return items

def make_items(username, quiz_name, item_no):
    sheet_count = get_sheet_count(username, quiz_name)
    corrections = get_corrections(username, quiz_name)
    corrections_for_i = [c[item_no] for c in corrections]
    items = [
                make_item(username, quiz_name, sheet_no, item_no, corrections_for_i[sheet_no]) 
                for sheet_no in range(1, sheet_count) # ignore first (blank) sheet
            ]
    return items

def make_item(username, quiz_name, sheet_no, item_no, correction):
    return {'src': "/item-img/{}/{}/{}/{}".format(username, quiz_name, sheet_no, item_no),
                 'sheet_no': sheet_no,
                 'item_no': item_no,
                 'username': username,
                 'quiz_name': quiz_name,
                 'value': correction
            }

def make_corrections(username, quiz_name):
    answer_key = get_answer_key(username, quiz_name)
    bounding_boxes = get_bounding_boxes_for_quiz(username, quiz_name) # bounding boxes for sample sheet (sheet_no 0)
    correction_values = get_corrections(username, quiz_name)
    sheet_count = get_sheet_count(username, quiz_name)
    item_count  = get_item_count(username, quiz_name)
    # make corectsoin
    cs = []
    
    for sheet_no in range(sheet_count):
        corrections_for_sheet = make_corrections_for_sheet(username, quiz_name, sheet_no, correction_values[sheet_no], bounding_boxes, answer_key, item_count)
        cs.extend(corrections_for_sheet)

    return cs



def make_corrections_for_sheet(username, quiz_name, sheet_no, corrections, bounding_boxes, answer_key, item_count):
    corr_boxes = zip(answer_key, corrections, bounding_boxes, range(item_count))
    corrections = []
    for correct_answer, correction_value, bounding_box, item_no in corr_boxes:
        id_classes = make_dom_id_classes(username, quiz_name, sheet_no, item_no)
        c = make_correction(id_classes, correct_answer, bounding_box, correction_value)
        corrections.append(c)
    return corrections


def make_correction(id_classes, correct_answer, bounding_box, correction_value):
    return {
            'id_classes': id_classes,
            'correct_answer' : correct_answer,
            'value': correction_value,
            'bounding_box': bounding_box
            }

def make_dom_id_classes(username, quiz_name, sheet_no, item_no):
    sheet_id_class = "sheet-" + username + "-" + quiz_name + "-" + str(sheet_no);
    item_id_class = "item-" + username + "-" + quiz_name + "-" + str(sheet_no) + "-" + str(item_no);
    return (sheet_id_class, item_id_class)

@app.template_filter('urlencode_component')
def urlencode_filter(s):
    s = s.encode('utf8')
    s = urllib.parse.quote(s, safe='')
    return s

## MARK models.py

def get_indeces_for_value(username, quiz_name, value):
    answer_key = get_answer_key(username, quiz_name)
    indeces = []
    for idx, val in enumerate(answer_key):
        if(val == value):
            indeces.append(idx)
    return indeces

# def get_answer_key(username, quiz_name):
#     filename = "./score_data/{0}/processed_quizzes/{1}/scoring/answer_key.json".format(username, quiz_name)
#     with open(filename) as data_file:    
#         data = json.load(data_file)
#     return data


def get_sheet_count(username, quiz_name):
    corrections = get_corrections(username, quiz_name)
    sheet_count = len(corrections)
    return sheet_count

def get_item_count(username, quiz_name):
    corrections = get_corrections(username, quiz_name)
    sheet_count = len(corrections)
    item_count = len(corrections[0])
    return item_count

# def get_corrections(username, quiz_name):
#     filename = "./score_data/{0}/processed_quizzes/{1}/scoring/corrections.csv".format(username, quiz_name)
#     rows = []
#     with open(filename) as f:
#         reader = csv.reader(f)
#         for row in reader:
#             ## throw out first two cols (col1 = student_id, col2 = average for this item)
#             rows.append(row[CORR_LEFT_OFFSET:])
#             #rows.append(row)
#     return rows

#def write_default_corrections(username, quiz_name, quiz_id, sheet_count, item_count):
#    filename = "score_data/{0}/processed_quizzes/{1}/scoring/corrections.csv".format(username, quiz_name, quiz_id)
#    scores = [['1' for item_no in range(item_count)] for sheet_no in range(sheet_count)]
#    with csv.open(filename):
#        writer = csv.writer(csvfile)
#        writer.writerows(scores)

def get_bounding_boxes_for_quiz(username, quiz_name):
    filename = "./score_data/{0}/processed_quizzes/{1}/scoring/cv_data.json".format(username, quiz_name)
    data = {}
    with open(filename) as data_file:    
        data = json.load(data_file)
    return data["bounding_boxes"]

