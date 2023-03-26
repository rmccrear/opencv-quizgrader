# create_quiz.py
# processes new quiz from pdf input

from flask import request, render_template, jsonify
from flask_login import login_required

from quizitemfinder.io import create_quiz_directory_structure, get_sheets_with_errors, save_hotspots
from quizitemfinder.db_models.roster import Roster
from quizitemfinder.process_quiz import do_process_quiz, do_pdf2jpg
from quizitemfinder.process_graded_sheets import save_graded_sheets_for_quiz, convert_graded_to_pdf

import time

from scripts.cv.main import do_command
# def fix_webapp(teacher_id, quiz_name):
#     do_command(teacher_id, quiz_name, "fix_webapp")

def setup_process_scanned_pdf(app):


    #@app.route("/api/v1/create_quiz/<username>/<semester>/<course>/<quiz_name>", methods=['POST'])
    #@login_required
    #def create_quiz_structure(username, semester, course, quiz_name):
    #    create_quiz_directory_structure(username, full_quiz_name)
    #    return True

    import re
    def fname2img_url(username, full_quiz_name, fname):
        m = re.search('(\d+)\.([a-zA-Z]+)$', fname)
        num = m.group(1)
        ext = m.group(2)
        return "//sheet-img/{}/{}/{}.{}".format(username, full_quiz_name, num, ext)

    @app.route("/api/v1/submit-pdf/<username>/<semester>/<course_name>/<quiz_name>", methods=['POST'])
    @login_required
    def submit_pdf(username, semester, course_name, quiz_name):
        full_quiz_name = "{}--{}--{}".format(semester, course_name, quiz_name)
        print('starting processing ' + full_quiz_name)
        create_quiz_directory_structure(username, full_quiz_name)
        f = request.files['quiz_pdf']
        f.save('./score_data/{}/processed_quizzes/{}/{}.pdf'.format(username, full_quiz_name, full_quiz_name))
        t1 = time.time()
        image_names = do_pdf2jpg(username, full_quiz_name)
        t2 = time.time()
        print('did pdf2jpg {} images in {} sec.'.format(len(image_names), t2-t1))
        image_urls = [fname2img_url(username, full_quiz_name, fname) for fname in image_names]
        # t3 = time.time()
        # fix_webapp(teacher_id, quiz_name)
        # t4 = time.time()
        # print('did fixwebapp {} sec.'.format(len(image_names), t3-t4))

        return jsonify(image_urls)

    @app.route("/crop-img/<username>/<quiz_name>/", methods=['GET', 'POST'])
    @login_required
    def crop_img(username, quiz_name):
        #fname = "{}--{}--{}".format(semester, course_name, quiz_name)
        #img_src = fname2img_url(username, semester, fname)
        if request.method == 'GET':
            return render_template("cropper.html", username=username, quiz_name=quiz_name)
        if request.method == 'POST':
            headers_rect = request.form['headers-rect'].split(",")
            items_rect = request.form['items-rect'].split(",")
            save_hotspots(username, quiz_name, headers_rect, items_rect)
            return "-".join(headers_rect) + "-".join(items_rect)
            # save_crop_rects(username, quiz_name, headers_rect, items_rect)
            # then go do (re)process_quiz

    @app.route("/new-quiz/<username>/", methods=['GET', 'POST'])
    @login_required
    def new_quiz(username):
        if request.method == 'GET':
            #return render_template("_quiz_form.html")
            semesters = Roster.all_semesters(username)
            return render_template("new_quiz.html", username=username, semesters=semesters)
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
    @login_required
    def reprocess_quiz(username, full_quiz_name):
        create_quiz_directory_structure(username, full_quiz_name)
        saved_pdf = './score_data/{}/processed_quizzes/{}/{}.pdf'.format(username, full_quiz_name, full_quiz_name)
        results = do_process_quiz(username, full_quiz_name, [], do_pdf_processing=False)
        error_sheet_nos = results["errors"]
        return render_template("quiz_complete.html",
                                   error_sheet_nos=error_sheet_nos,
                                   username=username,
                                   quiz_name=full_quiz_name)
        #return "<p>POSTED -- " + full_quiz_name +  "<p>errors: " + ", ".join([str(e) for e in results["errors"]]) + "<p> <a href='/quiz/{}/{}'> {} </a>".format(username, full_quiz_name, full_quiz_name)

    @app.route("/quiz-errors/<username>/<quiz_name>", methods=['GET'])
    @login_required
    def view_quiz_errors(username, quiz_name):
        error_sheet_nos = get_sheets_with_errors(username, quiz_name)
        return render_template("quiz_complete.html",
                                   error_sheet_nos=error_sheet_nos,
                                   username=username,
                                   quiz_name=quiz_name)



