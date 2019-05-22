# create_quiz.py
# processes new quiz from pdf input

from flask import request, render_template
from flask_login import login_required

from quizitemfinder.io import create_quiz_directory_structure, get_sheets_with_errors
from quizitemfinder.process_quiz import do_process_quiz
from quizitemfinder.process_graded_sheets import save_graded_sheets_for_quiz, convert_graded_to_pdf


def setup_process_scanned_pdf(app):

    @app.route("/new-quiz/<username>/", methods=['GET', 'POST'])
    @login_required
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

    

