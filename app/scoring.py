# scoring.py
from flask import Flask
from flask import send_file
from flask import render_template
from flask import request, Response, redirect, make_response, jsonify
from flask_login import login_required
import csv
import json
import urllib
app = Flask(__name__)

import glob
import os


from quizitemfinder.io import create_quiz_directory_structure, header_im_path, count_headers, count_sheets, get_roster, has_roster, set_student_ids_for_quiz, get_student_ids_for_quiz, set_scores_for_quiz, get_scores_for_quiz, get_answer_key, save_answer_key, get_corrections, error_sheet_path, error_corrected_sheet_path, get_sheets_with_errors, find_sheet_dims, is_quiz_finished, set_score_for_items, is_quiz_finished, get_predicted_student_ids
from quizitemfinder.process_quiz import do_process_quiz
from quizitemfinder.process_graded_sheets import save_graded_sheets_for_quiz, convert_graded_to_pdf
import numpy as np


def pointbiserialr(a,b):
    return np.corrcoef(a,b)[0][1];

def setup_scoring(app):

    def pbc_level(item_desc):
        if np.isnan(item_desc): return 'item-nan'
        elif item_desc > 0.30: return 'item-very-good'
        elif item_desc < 0.30 and item_desc > 0.20: return 'item-good'
        elif item_desc < 0.20 and item_desc > 0.10: return 'item-ok'
        elif item_desc < 0.10 : return 'item-bad'

    def percent_correct_level(percent_correct):
        if(percent_correct > 60):
            return '60-100'
        else:
            return '0-60'

    @app.route("/quiz-stats/<username>/<quiz_name>")
    def stats_for_quiz(username, quiz_name):
        answer_key = get_answer_key(username, quiz_name)
        corrections = get_corrections(username, quiz_name)
        cc = corrections
        dd = np.asarray(cc, dtype=np.float64, order='C')
        
        percent_correct_for_item = 100*np.sum(dd, 0)/len(dd)
        #percent_correct_for_item_as_str = map(lambda x: "{:.0f}".format(x), percent_correct_for_item)

        scores = np.sum(dd, 1)/len(dd[0])*100
        item_discrimination = list(map(lambda n: pointbiserialr(scores, dd[:,n]), range(len(dd[0]))))

        percent_correct_levels = list(map(percent_correct_level, percent_correct_for_item))
        pbc_levels = list(map(pbc_level, item_discrimination))
        tabular_data = [{'n': n, 'percent_correct': i[0], 'item_discr': i[1], 'item_discr_level': i[2], 'percent_correct_level': i[3], 'answer_key': i[4]} for n, i in enumerate(zip(percent_correct_for_item, item_discrimination, pbc_levels, percent_correct_levels, answer_key))]
        
        # item_discrimination_as_str = ["{:.2f}".format(i) for i in item_discrimination]

        return render_template("stats.html", percent_correct_for_item=percent_correct_for_item, item_discrimination=item_discrimination, username=username, quiz_name=quiz_name, tabular_data=tabular_data)




   # MARK: headers and student ids
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
        quiz_headers_with_dims = []
        bounding_boxes = get_bounding_boxes_for_sheets(username, quiz_name)
        for sheet_no in range(sheet_count) :
            header_bounding_boxes = bounding_boxes[sheet_no]["headers"]
            dims_for_headers = [bounding_box_to_dims(bounding_box) for bounding_box in header_bounding_boxes]
            hd = [ {
                      "username": username,
                      "quiz_name": quiz_name,
                      "sheet_no": sheet_no,
                      "dims": dims,
                      "header_no": i
                    } for i, dims in enumerate(dims_for_headers) ]
            headers = {
                      "username": username,
                      "quiz_name": quiz_name,
                      "sheet_no": sheet_no,
                      "imgs": [],
                      "data": ['' for i in  range(len(dims_for_headers))], #header count
                      "length": 0,
                      "dims_for_headers": hd
                    }
            quiz_headers.append(headers)    

        sheet_no2student_id = get_student_ids_for_quiz(username, quiz_name)
        
        predicted_student_ids = [''.join(arr) for arr in get_predicted_student_ids(username, quiz_name)]
        
        if(len(sheet_no2student_id ) < 1):
            app.logger.error('no student ids in place yet')
            #sheet_no2student_id = ['',''] + [s['student_id'] for s in roster]
            ids_in_roster = [s['student_id'] for s in roster]
            guesstimates = [guess_student_id(pp, ids_in_roster) for pp in predicted_student_ids[2:]]
            print(guesstimates)
            sheet_no2student_id = ['', ''] + guesstimates
        # sheet_no2student_id = get_sheets2student_ids(username, quiz_name)
        #if(len(sheet_no2student_id) < 1)):
        #    sheet_no2student_id = [s['student_id'] for s in s roster]
        return render_template("quiz_to_students_css.html", username=username, quiz_name=quiz_name, quiz_headers=quiz_headers, json_roster=json_roster, sheet_no2student_id=json.dumps(sheet_no2student_id), quiz_headers_with_dims=quiz_headers_with_dims, predicted_student_ids=json.dumps(predicted_student_ids))    



    def guess_student_id(prediction, roster):
        print(prediction)
        if(prediction in roster):
            return prediction
        elif(len(prediction) > 2):
            roster_last3 = [i[-3:] for i in roster]
            last3 = prediction[-3:]
            if(last3 in roster_last3):
                return last3
        else:
            return ''



    # MARK: scoring starts here
    @app.route("/quiz/<username>/<quiz_name>")
    @login_required
    def present_quiz(username, quiz_name):
        answer_key = get_answer_key(username, quiz_name)
        answers = sorted(list(set(answer_key)))
        item_count = get_item_count(username, quiz_name)
        item_nos = range(item_count)
        semester = 'semester'; course_name='course'
        has_answer_key = False
        has_student_ids_in_place = False
        has_been_finished = False
        has_roster_file = False
        if len(answers) > 0:
            has_answer_key = True
        if(len( get_student_ids_for_quiz(username, quiz_name) ) > 0):
            has_student_ids_in_place = True

        if(len(quiz_name.split('--')) > 2):
            semester = quiz_name.split('--')[0]
            course_name =  quiz_name.split('--')[1]
            has_roster_file = has_roster(username, semester, course_name)
        if(is_quiz_finished(username, quiz_name)):
            has_been_finished = True
        return render_template("present_quiz.html", answers=answers, username=username, quiz_name=quiz_name, item_nos=item_nos, course_name=course_name, semester=semester, has_answer_key=has_answer_key, has_student_ids_in_place=has_student_ids_in_place, has_been_finished=has_been_finished, has_roster_file=has_roster_file)    


    @app.route("/quiz-auto-grade/<username>/<quiz_name>", methods=['POST'] )
    @login_required
    def quiz_auto_grade(username, quiz_name):
        from quizitemfinder.steps.letterpredictor import LetterPredictor
        import quizitemfinder.steps.utils as utils
        from quizitemfinder.io import set_list_of_corrections
        quiz_ref = utils.QuizRef(username, quiz_name)
        predictor = LetterPredictor(quiz_ref)
        predictor.clean_items()
        items = predictor.predict()
        #corrections = get_corrections(username, quiz_name)
        #predictor.corrections2d(corrections)
        # need to get answer_key and do corrections
        list_of_corrections = [[item.sheet_no, item.item_no, item.score] for item in items if item.score == 0]
        set_list_of_corrections(username, quiz_name, list_of_corrections)
        return redirect('/quiz/{}/{}'.format(username, quiz_name))    

    @app.route("/quiz/<username>/<quiz_name>/<sheet_no>")
    @login_required
    def user_quiz(username, quiz_name, sheet_no):
        img_src = "/sheet-img/{0}/{1}/{2}.jpeg".format(username, quiz_name, sheet_no)
        return "<img src={}>".format(img_src)    

    @app.route("/sheet-img/<username>/<quiz_name>/<sheet_no>.jpeg")
    @login_required
    def serve_sheet_img(username, quiz_name, sheet_no):
        filename = "score_data/{0}/processed_quizzes/{1}/sheets/img-{2}.jpeg".format(username, quiz_name, sheet_no)
        return send_file(filename, mimetype='image/jpeg')     

    @app.route("/error-img/<username>/<quiz_name>/<sheet_no>.png")
    @login_required
    def serve_error_img(username, quiz_name, sheet_no):
        filename = "score_data/{0}/processed_quizzes/{1}/sheets/img-{2}.jpeg".format(username, quiz_name, sheet_no)
        filename = error_sheet_path(username, quiz_name, sheet_no)
        return send_file(filename, mimetype='image/jpeg')     

    @app.route("/error-corrected-img/<username>/<quiz_name>/<sheet_no>.png")
    @login_required
    def serve_error_corrected_img(username, quiz_name, sheet_no):
        filename = "score_data/{0}/processed_quizzes/{1}/sheets/img-{2}.jpeg".format(username, quiz_name, sheet_no)
        filename = error_corrected_sheet_path(username, quiz_name, sheet_no)
        return send_file(filename, mimetype='image/jpeg')     

    @app.route("/item-img/<username>/<quiz_name>/<sheet_no>/<item_no>")
    @login_required
    def serve_item_img(username, quiz_name, sheet_no, item_no):
        filename = "score_data/{0}/processed_quizzes/{1}/trimmed_img/l.{2}.i.{3}.png".format(username, quiz_name, sheet_no, item_no)
        return send_file(filename, mimetype='image/png')     

    @app.route("/header-img/<username>/<quiz_name>/<sheet_no>/<header_no>")
    @login_required
    def serve_header_img(username, quiz_name, sheet_no, header_no):
        filename = header_im_path(username, quiz_name, header_no, sheet_no) #"score_data/{0}/processed_quizzes/{1}/trimmed_img/l.{2}.i.{3}.png".format(username, quiz_name, sheet_no, item_no)
        return send_file(filename, mimetype='image/png')     

 
    @app.route("/save-students-for-quiz/<username>/<quiz_name>", methods=['POST'])
    @login_required
    def save_quiz_to_students(username, quiz_name):
        data = request.get_json()
        set_student_ids_for_quiz(username, quiz_name, data)
        return json.dumps(data)    
    

    ## throw out first two cols (col1 = student_id, col2 = average for this item)
    CORR_LEFT_OFFSET = 2
    # CORR_LEFT_OFFSET = 0
    # MARK: corrections
    @app.route("/corrections/set/<username>/<quiz_name>/<int:sheet_no>/<int:item_no>/<value>", methods=['GET'])
    @login_required
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

    @app.route("/corrections/set-items/<username>/<quiz_name>/", methods=['POST'])
    @login_required
    def set_corrections(username, quiz_name):
        items_in=request.get_json()
        items = [(i["sheet_no"], i["item_no"], i["value"]) for i in items_in]
        set_score_for_items(username, quiz_name, items)
        return '{"status": "OK"}'    

    @app.route("/corrections/get/<username>/<quiz_name>/<int:sheet_no>/<int:item_no>")
    @login_required
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

    def get_corrections(username, quiz_name):
        filename = "./score_data/{0}/processed_quizzes/{1}/scoring/corrections.csv".format(username, quiz_name)
        rows = []
        with open(filename) as f:
            reader = csv.reader(f)
            for row in reader:
                ## throw out first two cols (col1 = student_id, col2 = average for this item)
                rows.append(row[CORR_LEFT_OFFSET:])
                #rows.append(row)
        return rows       

    @app.route("/items/<username>/<quiz_name>/<int:item_no>")
    @login_required
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
    @login_required
    def serve_items_for_particular_answer(username, quiz_name,  answer_value):
        items = make_items_for_particular_answer(username, quiz_name,  answer_value)
        items_in_sheets = make_corrections(username, quiz_name)
        sheet_dims = find_sheet_dims(username, quiz_name, 0)
        answer_key = get_answer_key(username, quiz_name)
        next_item_url = False
        next_item_val = False
        possible_answers = list(set(answer_key))
        possible_answers.sort()
        if(possible_answers.index(answer_value)+1<len(possible_answers)):
            next_item_val = possible_answers[possible_answers.index(answer_value)+1]
            next_item_url = "/items-for-value/{}/{}/{}".format(username, quiz_name, next_item_val)

        return_values = dict(items=items, items_in_sheets=items_in_sheets, answer_value=answer_value, username=username, quiz_name=quiz_name, sheet_dims=sheet_dims, next_item_val=next_item_val, next_item_url=next_item_url)    

        if request.content_type != 'application/json':
            return render_template("correct_items.html", **return_values)
        else:
            return make_response(jsonify(return_values), 200)

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
        print(item_no)
        print(corrections)
        corrections_for_i = [c[item_no] for c in corrections]
        bounding_boxes = get_bounding_boxes_for_sheets(username, quiz_name) # bounding boxes for sample sheet (sheet_no 0)
        items = [
                    make_item(username, quiz_name, sheet_no, item_no, corrections_for_i[sheet_no], bounding_boxes[sheet_no]['items'][item_no])
                    for sheet_no in range(1, sheet_count) # ignore first (blank) sheet
                ]
        return items    

    def make_item(username, quiz_name, sheet_no, item_no, correction, bounding_box):
        return {'src': "/item-img/{}/{}/{}/{}".format(username, quiz_name, sheet_no, item_no),
                     'sheet_no': sheet_no,
                     'item_no': item_no,
                     'username': username,
                     'quiz_name': quiz_name,
                     'value': correction,
                     'dims': bounding_box_to_dims(bounding_box)
                }    

    def bounding_box_to_dims(bounding_box):
        bb = bounding_box
        return {
            "bounding_box": bb,
            "x": bb[0],
            "y": bb[1],
            "height": bb[3] - bb[1],
            "width":  bb[2] - bb[0]
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
                'bounding_box': bounding_box,
                'dims': bounding_box_to_dims(bounding_box)
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

    def get_bounding_boxes_for_sheets(username, quiz_name):
        filename = "./score_data/{0}/processed_quizzes/{1}/scoring/rectangles.json".format(username, quiz_name)
        data = None
        with open(filename) as data_file:    
            data = json.load(data_file)
        data_flat = [{}]*len(data)
        for i in range(len(data)):
            if data[i] is False:
                data[i] = data[0]
            # flatten
            data_flat[i]['items'] =   [ [ d[0][0], d[0][1], d[1][0], d[1][1] ] for d in data[i]['items']   ]
            data_flat[i]['headers'] = [ [ d[0][0], d[0][1], d[1][0], d[1][1] ] for d in data[i]['headers'] ]
        return data_flat
