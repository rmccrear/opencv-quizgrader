from quizitemfinder.io import quiz_loc

import subprocess, glob, os, time, re, shutil

# depends on poppler's pdftoppm being in path



def rename_sheets(username, quiz_name, sub_dir='sheets/', o_prefix='img-', o_suffix='.jpeg', i_search_glob='*.jpg', i_no_regex='img-(\d+)\.jpg'):
    #data_path = 'score_data'
    quiz_dir = quiz_loc(username, quiz_name)
    sheets_dir = quiz_dir + sub_dir
    for filepath in glob.iglob(os.path.join(sheets_dir, i_search_glob)):
        print(filepath)
        # rename img-01.jpg -> img-1.jpeg
        i = int(re.search(i_no_regex, filepath).groups()[-1])
        #filename2 = 'img-' + str(i-1) + '.jpeg'
        filename2 = o_prefix + str(i-1) + o_suffix
        filepath2 = sheets_dir + filename2
        os.rename(filepath, filepath2)

def rawpdf2imgs(username, quiz_name, img_format='jpeg', sub_dir='sheets/img'):
    data_path = 'score_data'
    pdf_path = data_path + "/{}/processed_quizzes/{}/{}.pdf".format(username, quiz_name, quiz_name)
    sheet_path = data_path + "/{}/processed_quizzes/{}/{}".format(username, quiz_name, sub_dir)
    if(img_format == 'jpeg'): opts = '-jpeg';
    if(img_format == 'tiff'): opts = '-tiff';
    cmd = ['pdftoppm', opts, pdf_path, sheet_path]
    subprocess.call(cmd)  
    time.sleep(1)
    rename_sheets(username, quiz_name)
    
def cp_pdf_to_quiz_dir(pdf_loc, username, quiz_name):
    data_path = 'score_data'
    pdf_path2 = data_path + "/{}/processed_quizzes/{}/{}.pdf".format(username, quiz_name, quiz_name)
    shutil.copy2(pdf_loc, pdf_path2)

def cp_graded_pdfs_to_quiz_dir(username, quiz_name):
    data_path = 'score_data'
    graded_pdf_name = "{}-graded.pdf".format(quiz_name)
    overlay_pdf_name = "{}-overlay.pdf".format(quiz_name)
    graded_path = data_path + "/{}/processed_quizzes/{}/sheets-graded/graded-sheets/graded-sheets.pdf".format(username, quiz_name)
    overlay_path = data_path + "/{}/processed_quizzes/{}/sheets-graded/graded-overlays/graded-overlays.pdf".format(username, quiz_name)
    dest_dir = data_path + "/{}/".format(username, quiz_name, quiz_name)
    shutil.copy2(graded_path, dest_dir + graded_pdf_name)
    shutil.copy2(overlay_path, dest_dir + overlay_pdf_name)
    