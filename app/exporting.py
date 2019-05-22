# exporting.py


from flask import Response, send_file, redirect
from flask_login import login_required

from quizitemfinder.io import set_scores_for_quiz, get_scores_for_quiz
from quizitemfinder.process_pdf import export_sheets_with_student_numbers
from quizitemfinder.process_graded_sheets import save_graded_sheets_for_quiz, convert_graded_to_pdf

def setup_exporting(app):
    @app.route("/quiz-scores/<username>/<quiz_name>.csv")
    @login_required
    def quiz_scores(username, quiz_name):
        set_scores_for_quiz(username, quiz_name)
        score_rows = get_scores_for_quiz(username, quiz_name)
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
