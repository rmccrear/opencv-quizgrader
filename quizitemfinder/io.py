import cv2
import glob
import json
import csv
import os

from PIL import Image

DATA_PATH = './score_data'
CORR_LEFT_OFFSET = 2 # offset in corrections file


#def sheet_loc(quiz_name, sheet_no, data_path):
#    path = data_path + "{}/sheets/img-{}.jpeg".format(quiz_name, sheet_no) 
#    return path

def quiz_loc(username, quiz_name, data_path=DATA_PATH):
    return "{}/{}/processed_quizzes/{}/".format(data_path, username, quiz_name)

#def user_loc(username, data_path=DATA_PATH):
#    return "{}/{}/".format(data_path, username)

def quizzes_for_user(username, data_path=DATA_PATH):
    path = "{}/{}/processed_quizzes/".format(data_path, username)
    dirs = os.listdir(path)
    #quizzes = [d for d in dirs if ('--' in d)]
    quizzes = [d for d in dirs if d[0] != '.']
    return quizzes

def sheet_loc(username, quiz_name, sheet_no, data_path=DATA_PATH):
    # quiz_location = quiz_loc(username, quiz_name).format(data_path, username, quiz_name)
    return quiz_loc(username, quiz_name, data_path=DATA_PATH) + "sheets/img-{}.jpeg".format(
        sheet_no
    )

def open_sheet_im(username, quiz_name, sheet_no, data_path=DATA_PATH):
    sheet_location = sheet_loc(username, quiz_name, sheet_no, data_path=DATA_PATH)
    return cv2.imread(sheet_location, cv2.IMREAD_GRAYSCALE)

def open_sheet_img(username, quiz_name, sheet_no, data_path=DATA_PATH):
    sheet_location = sheet_loc(username, quiz_name, sheet_no, data_path=DATA_PATH)
    return Image.open(sheet_location)

def count_sheets(username, quiz_name, data_path=DATA_PATH):
    quiz_path = quiz_loc(username, quiz_name, data_path=DATA_PATH) #.format(data_path, username, quiz_name)
    path = quiz_path + 'sheets/'
    return len(glob.glob(path + "*.jpeg"))


def header_im_path(username, quiz_name, header_no, sheet_no, data_path=DATA_PATH):
    quiz_path = quiz_loc(username, quiz_name) #.format(data_path, username, quiz_name)
    path = quiz_path + 'trimmed_img/header.{}.n.{}.png'.format(sheet_no, header_no)
    return path

def item_im_path(username, quiz_name, item_no, sheet_no, data_path=DATA_PATH):
    quiz_path = quiz_loc(username, quiz_name) #.format(data_path, username, quiz_name)
    path = quiz_path + 'trimmed_img/l.{}.i.{}.png'.format(sheet_no, item_no)
    return path

def letter_im_path(username, quiz_name, item_no, sheet_no, data_path=DATA_PATH):
    quiz_path = quiz_loc(username, quiz_name) #.format(data_path, username, quiz_name)
    path = quiz_path + 'trimmed_img/letter.{}.i.{}.png'.format(sheet_no, item_no)
    return path

def error_sheet_path(username, quiz_name, sheet_no, data_path=DATA_PATH):
    quiz_path = quiz_loc(username, quiz_name) #.format(data_path, username, quiz_name)
    path = quiz_path + 'error-img/error-sheet.{}.png'.format(sheet_no)
    return path
def error_corrected_sheet_path(username, quiz_name, sheet_no, data_path=DATA_PATH):
    quiz_path = quiz_loc(username, quiz_name) #.format(data_path, username, quiz_name)
    path = quiz_path + 'error-img/corrected-sheet.{}.png'.format(sheet_no)
    return path

def save_header_im(header_im, username, quiz_name, header_no, sheet_no, data_path=DATA_PATH):
    p = header_im_path(username, quiz_name, header_no, sheet_no, data_path=DATA_PATH)
    cv2.imwrite(p, header_im)

def save_item_im(item_im, username, quiz_name, item_no, sheet_no, data_path=DATA_PATH):
    p = item_im_path(username, quiz_name, item_no, sheet_no, data_path=DATA_PATH)
    cv2.imwrite(p, item_im)

def save_letter_im(letter_im, username, quiz_name, item_no, sheet_no, data_path=DATA_PATH):
    p = letter_im_path(username, quiz_name, item_no, sheet_no, data_path=DATA_PATH)
    cv2.imwrite(p, letter_im)

def save_error_sheet_img(sheet_img, username, quiz_name, sheet_no, data_path=DATA_PATH):
    p = error_sheet_path(username, quiz_name, sheet_no, data_path=DATA_PATH)
    sheet_img.save(p)

def save_error_corrected_sheet_img(sheet_img, username, quiz_name, sheet_no, data_path=DATA_PATH):
    p = error_corrected_sheet_path(username, quiz_name, sheet_no, data_path=DATA_PATH)
    sheet_img.save(p)
    
def count_headers(username, quiz_name):
    # discover how many headers we have...
    header_count = 0
    sheet_no = 0 # <- const
    path = header_im_path(username, quiz_name, header_count, sheet_no)
    while(os.path.isfile(path)):
        header_count += 1
        path = header_im_path(username, quiz_name, header_count, sheet_no)
    return header_count

def get_roster(username, semester, course, data_path=DATA_PATH):
    path = '{data_path}/{username}/my_courses/{semester}/{course}/roster.csv'.format(data_path=data_path, username=username, semester=semester, course=course)
    with open(path, 'r') as f:
        reader = csv.reader(f)
        next(reader) # throw out headers
        students = []
        for row in reader:
            student = {
                        "student_id": row[0],
                        "name": row[1],
                        "email": row[2]
                    }
            students.append(student)
    return students

def set_student_ids_for_quiz(username, quiz_name, student_ids):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/corrections.csv'
    rows = read_csv_file(path)
    print(rows)
    for i in range(len(student_ids)):
        rows[i][0] = student_ids[i]
    #write_csv_file(path, rows)
    with open(path, 'w') as outfile:
        wr = csv.writer(outfile)        ####, quoting = csv.QUOTE_MINIMAL, dialect='excel')
        for row in rows:
            wr.writerow(row)
            
def get_student_ids_for_quiz(username, quiz_name):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/corrections.csv'
    rows = read_csv_file(path)
    student_ids = []
    has_them = False
    for i in range(len(rows)):
        if(rows[i][0]): has_them = True
        student_ids.append(rows[i][0])
    if(has_them):
        return student_ids
    else: 
        return []

def set_scores_for_quiz(username, quiz_name):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/corrections.csv'
    rows = read_csv_file(path)
    for i in range(len(rows)):
        corrections = [int(c) for c in rows[i][2:]]
        score = 100 * sum(corrections) / len(corrections)
        score_str = "{:.1f}".format(score)
        # if it is an int, don't use decimal places
        if(score == int(score)):
            score_str = "{:.0f}".format(score)
        rows[i][1] = score_str
    with open(path, 'w') as outfile:
        wr = csv.writer(outfile)        ####, quoting = csv.QUOTE_MINIMAL, dialect='excel')
        for row in rows:
            wr.writerow(row)

def get_scores_for_quiz(username, quiz_name):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/corrections.csv'
    rows = read_csv_file(path)
    for i in range(len(rows)):
        rows[i] = rows[i][:2]
    return rows

def get_answer_key(username, quiz_name):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/answer_key.json'
    with open(path) as data_file:    
        data = json.load(data_file)
    return data

def save_answer_key(username, quiz_name, answer_key):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/answer_key.json'
    with open(path, 'w') as data_file:
        data_str = json.dump(answer_key, data_file)

def get_CV_data(username, quiz_name):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/cv_data.json'
    with open(path) as data_file:    
        data = json.load(data_file)
    return data

def get_corrections(username, quiz_name):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/corrections.csv'
    rows = []
    with open(path) as f:
        reader = csv.reader(f)
        for row in reader:
            ## throw out first two cols (col1 = student_id, col2 = average for this item)
            rows.append(row[CORR_LEFT_OFFSET:])
            #rows.append(row)
    return rows

def get_item_count(username, quiz_name):
    return int(get_CV_data(username, quiz_name)["item_count"])

def get_sheets_with_errors(username, quiz_name):
    return get_CV_data(username, quiz_name)["sheets_with_errors"]

def save_rects(username, quiz_name, rects):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/rectangles.json'
    with open(path, "w") as outfile:
        json.dump(rects, outfile)

def open_rects(username, quiz_name):
    quiz_path = quiz_loc(username, quiz_name)
    path = quiz_path + 'scoring/rectangles.json'
    rects = []
    with open(path) as outfile:
        rects = json.load(outfile)
    return rects





#def set_correction_in_2d_array(corrections, sheet_no, item_no, value):
#    corrections_path = quiz_path + 'scoring/corrections.csv'
#    rows = corrections
#    rows[sheet_no][item_no + CORR_LEFT_OFFSET] = value

def set_list_of_corrections(username, quiz_name, correction_list):
    quiz_path = quiz_loc(username, quiz_name)
    corrections_path = quiz_path + 'scoring/corrections.csv'
    #filename = "score_data/{0}/processed_quizzes/{1}/scoring/corrections.csv".format(username, quiz_name)
    rows = []
    with open(corrections_path, mode="r") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
        corrections = rows
        for sheet_no, item_no, value in correction_list:
            rows[sheet_no][item_no + CORR_LEFT_OFFSET] = value
    #print(rows)
    with open(corrections_path, mode='w') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return value

#def item_path(sheet_no, item_no, quiz_name, data_path="./data/processed-quizzes/"):
#    p = data_path  + "{}/l.{}.i.{}.png".format(quiz_name, sheet_no, item_no)
#    return p

#def letter_path(sheet_no, item_no, quiz_name, data_path="./data/processed-quizzes/"):
#    p = data_path  + "{}/s.{}.i.{}.png".format(quiz_name, sheet_no, item_no)
#    return p



    
#def save_letter(letter_im, sheet_no, item_no, quiz_name, data_path="./data/processed-quizzes/"):
#    #p = data_path  + "{}/s.{}.i.{}.png".format(quiz_name, sheet_no, item_no)
#    p = letter_path(sheet_no, item_no, quiz_name, data_path=data_path)
#    cv2.imwrite(p, letter_im)






#def count_items_in_quiz(quiz_name, data_path="./data/processed-quizzes/"):
#    default_sheet = open_sheet_im(quiz_name, sheet_no=0, data_path=data_path)
#    rects = find_items_in_sheet_im(default_sheet)
#    return len(rects["items"])


def find_sheet_dims(username, quiz_name, sheet_no, data_path=DATA_PATH):
    sheet_im = open_sheet_im(username, quiz_name, sheet_no, data_path=data_path)
    SHEET_WIDTH = sheet_im.shape[1]; SHEET_HEIGHT=sheet_im.shape[0];
    return {'width': SHEET_WIDTH, 'height': SHEET_HEIGHT}

import os
def ensure_dir(file_path):
    d = os.path.dirname(file_path)
    if not os.path.isdir(d):
        print('creating {}'.format(d))
        os.makedirs(d)
    else:
        print('dir already exists: {}'.format(d))

def create_quiz_directory_structure(username, quiz_name):
    quiz_path = quiz_loc(username, quiz_name)
    print(quiz_path + 'scoring')
    ensure_dir(quiz_path)
    ensure_dir(quiz_path + 'scoring/')
    ensure_dir(quiz_path + 'sheets/')
    ensure_dir(quiz_path + 'sheets-graded/')
    ensure_dir(quiz_path + 'trimmed_img/')
    ensure_dir(quiz_path + 'error-img/')
    ensure_dir(quiz_path + 'sheets-graded/')
    ensure_dir(quiz_path + 'sheets-graded/graded-overlays/')
    ensure_dir(quiz_path + 'sheets-graded/graded-sheets/')


def read_csv_file(path):
    rows = []
    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows

## BUG: check this and the below uses of it. it needs an open before it
#def write_csv_file(path, lists):
#    wr = csv.writer(path, quoting = csv.QUOTE_MINIMAL, dialect='excel')
#    for row in lists:
#        wr.writerow(row)
    
# write initial data files for quiz   
# import os.path
def write_cv_data(username, quiz_name, cv_data, answer_key, corrections):
    quiz_path = quiz_loc(username, quiz_name)
    cv_path = quiz_path + 'scoring/cv_data.json'
    with open(cv_path, 'w') as outfile:
        print(cv_path)
        json.dump(cv_data, outfile)

    answer_path = quiz_path + 'scoring/answer_key.json'
    if not os.path.isfile(answer_path):
        with open(answer_path, 'w') as outfile:
            print(answer_path)
            json.dump(answer_key, outfile)    

    corrections_path = quiz_path + 'scoring/corrections.csv'
    if not os.path.isfile(corrections_path):
        with open(corrections_path, 'w') as outfile:
            # write_csv_file(outfile, corrections)
            wr = csv.writer(outfile, quoting = csv.QUOTE_MINIMAL, dialect='excel')
            for row in corrections:
                wr.writerow(row)

