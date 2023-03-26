# exporting.py


from flask import Response, send_file, redirect, render_template, request, make_response, jsonify
from flask_login import login_required

from quizitemfinder.io import set_scores_for_quiz, get_scores_for_quiz, quizzes_for_user
from quizitemfinder.db_models.roster import Roster
from quizitemfinder.process_pdf import export_sheets_with_student_numbers
from quizitemfinder.process_graded_sheets import save_graded_sheets_for_quiz, convert_graded_to_pdf

from io import StringIO
import csv
import re

def setup_exporting(app):

    @app.route("/semesters/<username>", methods=['GET'])
    @login_required
    def semsters(username):
        #sems = get_semesters(username)
        sems = Roster.all_semesters(username)
        return render_template('list_semesters.html', username=username, semesters=sems)

    @app.route("/my-courses/<username>/<semester>", methods=['GET', 'POST'])
    @login_required
    def list_courses(username, semester):
        #courses = get_courses(username, semester)
        courses = Roster.all_courses(username, semester)
        data = request.get_json()
        if(data is not None):
            return jsonify(courses)
        else:
            return render_template('list_courses.html', username=username, semester=semester, courses=courses)

    @app.route("/my-quizzes-for-course/<username>/<semester>/<course>", methods=['GET', 'POST'])
    @login_required
    def list_quizzes(username, semester, course):
        prefix = "{}--{}--".format(semester, course)
        quiz_names = quizzes_for_user(username)
        regex = "^{}([\w-]+)$".format(prefix)
        print(regex)
        print(re.match("[a-zA-Z]+", quiz_names[0]))
        matches = [re.search(regex, quiz_name).group(1) for quiz_name in quiz_names if re.match(regex, quiz_name)]
        print(quiz_names)
        print(matches)
        return jsonify(matches)


    @app.route("/roster-update", methods=['POST'])
    @login_required
    def post_roster():
        username = request.form.get('username')
        semester = request.form.get('semester')
        course_name = request.form.get('courseName')
        roster_csv = request.form.get('rosterCSV')
        #roster_file = StringIO(roster_csv)
        #roster_data = list(csv.reader(roster_file))
        roster = None
        try:
            roster = Roster(username, semester, course_name)
        except Exception as e:
            return make_response(jsonify({"message": str(e)}), 400)

        roster.set_roster(roster_csv)
        #save_roster(username, semester, course_name, roster_data)
        return Response(status=200)


    @app.route("/roster-create/<username>")
    @app.route("/roster-create/<username>/<semester>")
    @login_required
    def create_roster(username, semester=None):
        my_csv = "student id,name,email"
        return render_template('create_roster_csv.html', csv=my_csv, username=username, semester=semester)

    @app.route("/roster/<username>/<semester>/<course_name>")
    @login_required
    def update_roster(username, semester, course_name):
        roster_model = Roster(username, semester, course_name)
        roster_arr = roster_model.get_roster()
        rows = ["{}\t{}\t{}".format(item["student_id"], item["name"], item["email"]) for item in  roster_arr]
        rows.insert(0, "student_id\tname\temail")
        my_csv = "\n".join(rows)
        return render_template('create_roster_csv.html', csv=my_csv, username=username, semester=semester, course_name=course_name)


    @app.route("/quiz-scores/<username>/<quiz_name>.csv")
    @login_required
    def quiz_scores(username, quiz_name):
        set_scores_for_quiz(username, quiz_name)
        score_rows = get_scores_for_quiz(username, quiz_name)
        score_rows = score_rows[2:] # remove model and key pages
        score_str = "\n".join([",".join(row) for row in score_rows])
        # csv_path = 'score_data/{}/processed_quizzes/{}/scoring/corrections.csv'.format(username, quiz_name)
        return Response(score_str, mimetype='text/csv')
        # return send_file(csv_path, mimetype='text/csv')


    import time
    @app.route("/finish-quiz/<username>/<quiz_name>")
    @login_required
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
    @login_required
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
