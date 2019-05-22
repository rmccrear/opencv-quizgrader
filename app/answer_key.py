# answer_key.py

from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
import json

from quizitemfinder.io import create_quiz_directory_structure, header_im_path, count_headers, count_sheets, get_roster, set_student_ids_for_quiz, get_student_ids_for_quiz, set_scores_for_quiz, get_scores_for_quiz, get_answer_key, save_answer_key, get_corrections, error_sheet_path, error_corrected_sheet_path, get_sheets_with_errors, find_sheet_dims, is_quiz_finished, set_score_for_items
from quizitemfinder.process_quiz import do_process_quiz
from quizitemfinder.process_graded_sheets import save_graded_sheets_for_quiz, convert_graded_to_pdf




def get_bounding_boxes_for_quiz(username, quiz_name):
    filename = "./score_data/{0}/processed_quizzes/{1}/scoring/cv_data.json".format(username, quiz_name)
    data = {}
    with open(filename) as data_file:    
        data = json.load(data_file)
    return data["bounding_boxes"]

def bounding_box_to_dims(bounding_box):
    bb = bounding_box
    return {
        "bounding_box": bb,
        "x": bb[0],
        "y": bb[1],
        "height": bb[3] - bb[1],
        "width":  bb[2] - bb[0]
    }


def get_item_count(username, quiz_name):
    corrections = get_corrections(username, quiz_name)
    sheet_count = len(corrections)
    item_count = len(corrections[0])
    return item_count



def setup_answer_key(app):
    @app.route("/quiz-answer-key/<username>/<quiz_name>", methods=['GET', 'POST'] )
    @login_required
    def quiz_answer_key(username, quiz_name):
        #if current_user.get_id() != username:
        #    return redirect(url_for('login_user_route'))
        sheet_no = 1 # answer key
        item_count = get_item_count(username, quiz_name)
        answer_key = get_answer_key(username, quiz_name)
        have_saved_answer_key = False
        has_auto_predicted_answer_key = False
        items = []
    
        if request.method == 'POST':
            answer_key = []
            for item_no in range(item_count):
                key_name = "answer_" + str(item_no)
                val = request.form.get(key_name, False)
                answer_key.append(val if val else '')
            save_answer_key(username, quiz_name, answer_key)
    
        if len(answer_key) < 1:
            # todo: check if we don't have an ml model already
            from quizitemfinder.steps.letterpredictor import LetterPredictor
            import quizitemfinder.steps.utils as utils
            try:
                predictor = LetterPredictor(utils.QuizRef(username, quiz_name), has_answers=False)
                answer_key = predictor.predict_answer_key()
                has_auto_predicted_answer_key = True
            except:
                print("error in answer key processing")
        else:
            has_auto_predicted_answer_key = True
            have_saved_answer_key = True
    
        bounding_boxes = get_bounding_boxes_for_quiz(username, quiz_name) 
    
        for item_no in range(item_count):
            ans = answer_key[item_no] if item_no < len(answer_key) else ''
            items.append( {'src': "/item-img/{}/{}/{}/{}".format(username, quiz_name, sheet_no, item_no),
                     'sheet_no': sheet_no,
                     'item_no': item_no,
                     'username': username,
                     'quiz_name': quiz_name,
                     'value': ans,
                     'dims': bounding_box_to_dims(bounding_boxes[item_no])
                } )
        return render_template("answer_key.html", username=username, quiz_name=quiz_name, items=items, item_count=len(items), have_saved_answer_key=have_saved_answer_key, has_auto_predicted_answer_key=has_auto_predicted_answer_key)
