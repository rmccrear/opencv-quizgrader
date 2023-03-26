from quizitemfinder.io import quiz_loc, get_roster, get_scores_for_quiz

import subprocess, glob, os, time, re, shutil

# depends on poppler's pdftoppm being in path

class PDFProcessor:
    def __init__(self, username, quiz_name, format="jpeg"):
        if(format == "jpeg"):
            self.img_format = format
            self.o_suffix = '.jpeg'
            self.i_search_glob = "*.jpg"
        if(format == "tiff"):
            self.img_format = format
            self.o_suffix = '.tiff'
            self.i_search_glob = "*.tiff"

    def rename_sheets(self):
        return rename_sheets(self.username, self.quiz_name, o_prefix=self.o_prefix, i_search_glob=self.i_search_glob)

    def rawpdf2imgs(username, quiz_name, img_format='jpeg', sub_dir='sheets/img'):
        return rawpdf2imgs(self.username, self.quiz_name, img_format=self.img_format)


def rename_sheets(username, quiz_name, sub_dir='sheets/', o_prefix='img-', o_suffix='.jpeg', i_search_glob='*.jpg', i_no_regex='img-(\d+)\.jpg'):
    #data_path = 'score_data'
    quiz_dir = quiz_loc(username, quiz_name)
    sheets_dir = quiz_dir + sub_dir
    sheet_names = []
    for filepath in glob.iglob(os.path.join(sheets_dir, i_search_glob)):
        # rename img-01.jpg -> img-1.jpeg
        i = int(re.search(i_no_regex, filepath).groups()[-1])
        #filename2 = 'img-' + str(i-1) + '.jpeg'
        filename2 = o_prefix + str(i-1) + o_suffix
        sheet_names.append(filename2)
        filepath2 = sheets_dir + filename2
        os.rename(filepath, filepath2)
    return sheet_names

def rawpdf2imgs(username, quiz_name, img_format='jpeg', sub_dir='sheets/img'):
    data_path = 'score_data'
    pdf_path = data_path + "/{}/processed_quizzes/{}/{}.pdf".format(username, quiz_name, quiz_name)
    sheet_path = data_path + "/{}/processed_quizzes/{}/{}".format(username, quiz_name, sub_dir)
    if(img_format == 'jpeg'): opts = '-jpeg';
    if(img_format == 'tiff'): opts = '-tiff';
    cmd = ['pdftoppm', opts, pdf_path, sheet_path]
    t1 = time.time()
    subprocess.call(cmd)  
    t2 = time.time()
    print("did pdftoppm in {} sec.".format(t2-t1))
    time.sleep(1)
    t1 = time.time()
    image_names = rename_sheets(username, quiz_name)
    t2 = time.time()
    print('did rename sheets in {} sec'.format(t2-t1))
    return image_names

    
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
    

def export_sheets_with_student_numbers(username, quiz_name):
    #roster = get_roster(username, semester, course)
    scores = get_scores_for_quiz(username, quiz_name)
    quiz_path = quiz_loc(username, quiz_name)
    for i in range(2, len(scores)):
        print(scores[i])
        stu_id = scores[i][0]
        if(len(stu_id) > 0):
            graded_sheet_loc = quiz_path + "/sheets-graded/graded-sheets/graded-sheet-{}.jpeg".format(str(i))
            student_id_sheet_loc = quiz_path + "/sheets-graded/graded-id-sheets/{}.jpg".format(stu_id)
            shutil.copy2(graded_sheet_loc, student_id_sheet_loc)
