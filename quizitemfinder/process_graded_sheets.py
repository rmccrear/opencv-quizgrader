from os import path
import json
import csv
from PIL import Image, ImageDraw, ImageFont
import subprocess

import fontconfig

import quizitemfinder.io as io

# FONT_PATH = path.join('/System/Library/Fonts', 'NoteWorthy.ttc')
DATA_PATH = path.join('/Users/robertmccreary/Documents/code/proj/python/quiz_grader_server_python/score_data')

font_preference = ['NoteWorthy', 'Gamja Flower', 'arial']
def get_font_path(font_preference=font_preference):
    path = None
    n = 0
    while n<len(font_preference) and path is None:
        font_family = font_preference[n]
        fonts = fontconfig.query(family=font_family ,lang='en')
        if(len(fonts)>1):
            path = fonts[0].file
        n = n+1
    if(path is None):
        raise Exception('Could not find font. Tried [{}]'.format(", ".join(font_preference)))
    return path
FONT_PATH = get_font_path()


def score_position_and_font_size(username, quiz_name):
    bb = get_bounding_boxes_for_quiz(username, quiz_name)[0] # first item's box
    bb_top  = bb[1]
    bb_left = bb[0]
    bb_height = bb[3] - bb[1]
    
    #font_size = 2
    target_pixels_size = bb_height/2                 # half of box height
    #font = ImageFont.truetype(FONT_PATH, font_size)
    #while(font.getsize("00%")[1] < target_pixels_size):
    #    font_size += 1
    #    font = ImageFont.truetype(FONT_PATH, font_size)
    #font_size -= 1
    font_size = calc_font_size_for_height_in_px(FONT_PATH, target_pixels_size)
    
    score_pos = [bb_left + 2, bb_top - int(target_pixels_size*2)]
    return {
        "score_pos": score_pos,
        "font_size": font_size
    }

def student_id_position_and_font_size(username, quiz_name, student_id_header_no):
    bb = get_header_boxes_for_quiz(username, quiz_name)[2]
    bb_top     = find_top_of_box(bb)
    bb_left    = find_left_of_box(bb)
    bb_bottom  = find_bottom_of_box(bb)
    bb_height  = find_height_of_box(bb)  #bb_height = bb_bottom - bb_top #bb[3] - bb[1]
    font_size = 2
    target_pixels_size = bb_height/student_id_header_no                 # 1/4 of box height
    #font = ImageFont.truetype(FONT_PATH, font_size)
    #while(font.getsize("00%")[1] < target_pixels_size):
    #    font_size += 1
    #    font = ImageFont.truetype(FONT_PATH, font_size)
    #font_size -= 1
    font_size = calc_font_size_for_height_in_px(FONT_PATH, target_pixels_size)
    
    #pos = [bb_left + 2, bb_top - int(target_pixels_size*2)]
    pos = [bb_left + 5, bb_bottom + int(target_pixels_size/2)]
    return {
        "pos": pos,
        "font_size": font_size
    }  

# utility function to add two points together
def add_pts(a, b):
    return [a[0]+b[0], a[1]+b[1]]

def find_height_of_box(box): return box[3] - box[1];
def find_width_of_box(box):  return box[2] - box[0];
def find_top_of_box(box):    return box[1];
def find_left_of_box(box):   return box[0]
def find_bottom_of_box(box): return box[3]

def calc_font_size_for_height_in_px(font_path, target_pixels_size):
    font_size = 2 # start at 2pts
    font = ImageFont.truetype(FONT_PATH, font_size)
    while(font.getsize("00%")[1] < target_pixels_size):
        font_size += 1
        font = ImageFont.truetype(FONT_PATH, font_size)
    font_size -= 1
    return font_size

def marking_position_and_font_size(username, quiz_name):
    bb = get_bounding_boxes_for_quiz(username, quiz_name)[0] # first item's box
    bb_top  = bb[1]
    bb_left = bb[0]
    bb_height = find_height_of_box(bb) # bb[3] - bb[1]
    bb_width  = find_width_of_box(bb) # bb[2] - bb[0]
    
    font_size = 2
    target_pixels_size = bb_height/2            # half of box height
    font = ImageFont.truetype(FONT_PATH, font_size)
    while(font.getsize("X")[1] < target_pixels_size): # height
        font_size += 1
        font = ImageFont.truetype(FONT_PATH, font_size)
    font_size -= 1
    
    font_height = font.getsize("X")[1]
    font_width = font.getsize("X")[0]
    return {
        "offsets": {
            "right_offset": [bb_width - int(font_width*1.5), int(font_height*.2)],
            "left_offset":  [int(font_width*.25), int(font_height*.2)]
        },
        "font_size": font_size
    }


def get_bounding_boxes_for_quiz(username, quiz_name):
    data = io.get_CV_data(username, quiz_name)
    return data["bounding_boxes"]

def get_header_boxes_for_quiz(username, quiz_name):
    data = io.get_CV_data(username, quiz_name)
    return data["header_boxes"]


def get_answer_key(username, quiz_name):
    return io.get_answer_key(username, quiz_name)

def get_corrections(username, quiz_name):
    return io.get_corrections(username, quiz_name)


def get_id_and_score(username, quiz_name):
    return io.get_scores_for_quiz(username, quiz_name)
    #file_path = path.join(DATA_PATH, username, 'processed_quizzes', quiz_name, 'scoring', 'corrections.csv')
    ##filename = "./score_data/{0}/processed_quizzes/{1}/scoring/corrections.csv".format(username, quiz_name)
    #rows = []
    #with open(file_path) as f:
    #    reader = csv.reader(f)
    #    for row in reader:
    #        rows.append(row[:2])
    #return rows


def get_sheet_count(username, quiz_name):
    return io.count_sheets(username, quiz_name)
    #corrections = get_corrections(username, quiz_name)
    #sheet_count = len(corrections)
    #return sheet_count

def get_sheet_img(username, quiz_name, sheet_no):
    return io.open_sheet_img(username, quiz_name, sheet_no)
    #file_path = path.join(DATA_PATH, username, 'processed_quizzes', quiz_name, 'sheets', 'img-' + str(sheet_no) + '.jpeg')
    #img = Image.open(file_path)
    #return img



FONT_SIZE = 25
def draw_box(sheet_img, bb):
    draw = ImageDraw.Draw(sheet_img)
    draw.rectangle(bb, outline='red')
    del draw
    return sheet_img

def draw_boxes(sheet_img, bounding_boxes, color='red'):
    draw = ImageDraw.Draw(sheet_img)
    for bb in bounding_boxes:
        draw.rectangle(bb, outline=color)
    del draw
    return sheet_img

def draw_answer(sheet_img, pt, answer, font_size, color=(200,0,0,128)):
    draw = ImageDraw.Draw(sheet_img)
    # get a font
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw.text(pt, answer, font=font, fill=color)
    return sheet_img

def draw_answers(sheet_img, bounding_boxes, answer_key, corrections, font_size, offsets):
    bb_ans = zip(bounding_boxes, answer_key, corrections)
    # draw_boxes(sheet_img, bounding_boxes, 'black')
    for bb, answer, correction in bb_ans:
        #correction_spot = [bb[2]-20, bb[1]] #offsets["right_offset"]
        bb_pnt = [bb[0], bb[1]]
        correction_spot = add_pts(bb_pnt, offsets["right_offset"]) # [bb[2] + offsets["right_offset"][0], bb[1] + offsets["right_offset"][1]]
        correction_color = (200,0,0,128)
        if(correction == 0 or correction == '0'):
            draw_answer(sheet_img, correction_spot, 'X', font_size, correction_color)
        else:
            correction_color = (0,200,128)
            #draw_answer(sheet_img, correction_spot, 'O', font_size, correction_color) # '\u2714'
        ans_bb = add_pts(bb_pnt, offsets["left_offset"]) # [bb[2] + offsets["left_offset"][0], bb[1] + offsets["left_offset"][1]]
        draw_answer(sheet_img, ans_bb, answer, font_size, color=correction_color)
    return sheet_img

def draw_answers_for_quiz(username, quiz_name, on_blank=False):
    sheet_count = get_sheet_count(username, quiz_name)
    corrections = get_corrections(username, quiz_name)
    id_and_score = get_id_and_score(username, quiz_name)
    answer_key = get_answer_key(username, quiz_name)
    bounding_boxes = get_bounding_boxes_for_quiz(username, quiz_name)
    sheet_imgs = []
    s = score_position_and_font_size(username, quiz_name)
    score_font_size = s["font_size"]; score_pos = s["score_pos"]
    id_fonts = student_id_position_and_font_size(username, quiz_name, 2)
    id_font_size = id_fonts["font_size"]; id_pos = id_fonts["pos"]
    m = marking_position_and_font_size(username, quiz_name)
    marking_font_size = m["font_size"]; marking_offsets = m["offsets"]
    for sheet_no in range(sheet_count):
        sheet_img = get_sheet_img(username, quiz_name, sheet_no)
        if(on_blank):
            sheet_img = Image.new('RGB', sheet_img.size, color='white')
        corrections_for_sheet = corrections[sheet_no]
        draw_answers(sheet_img, bounding_boxes, answer_key, corrections_for_sheet, marking_font_size, marking_offsets)
        #score = calculate_score(corrections[sheet_no])
        score = id_and_score[sheet_no][1]
        student_id = id_and_score[sheet_no][0]
        draw_score(sheet_img, score, score_pos,score_font_size)
        draw_student_id(sheet_img, student_id, id_pos, id_font_size)
        sheet_imgs.append(sheet_img)
    return sheet_imgs

def draw_score(sheet_img, score_str, position, font_size):
    #score_str = "Score: {0:1.0f}%".format(score)
    draw = ImageDraw.Draw(sheet_img)
    # get a font
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw.text(position, "{}%".format(score_str), font=font, fill="red")

def draw_student_id(sheet_img, student_id, position, font_size):
    draw = ImageDraw.Draw(sheet_img)
    # get a font
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw.text(position, "{}".format(student_id), font=font, fill="black")  
    
#def calculate_score(corrections):
#    # weights
#    count = len(corrections[2:])
#    tot = sum(map(lambda x: int(x), corrections[2:]))
#    return tot/count*100

# trim off padding so it aligns with printed one
def trim_padding_on_sheet(sheet_img):
    width = sheet_img.size[0]
    height = sheet_img.size[1]
    return sheet_img.crop(
       (5,
        5,
        width-5,
        height-5
       )
    )

def save_graded_sheets_for_quiz(username, quiz_name):
    quiz_dir = io.quiz_loc(username, quiz_name)
    graded_sheets = draw_answers_for_quiz(username, quiz_name)
    for sheet_no, graded_sheet in enumerate(graded_sheets):
        file_path = path.join(quiz_dir, 'sheets-graded', 'graded-sheets','graded-sheet-' + str(sheet_no) + '.jpeg')
        graded_sheet.save(file_path, "JPEG")
    graded_sheets = draw_answers_for_quiz(username, quiz_name, on_blank=True)
    for sheet_no, graded_sheet in enumerate(graded_sheets):
        #file_path = path.join(DATA_PATH, username, 'processed_quizzes', quiz_name, 'sheets-graded', 'graded-overlays','graded-overlay-' + str(sheet_no) + '.jpeg')
        file_path = path.join(quiz_dir, 'sheets-graded', 'graded-overlays','graded-overlay-' + str(sheet_no) + '.jpeg')
        graded_sheet = trim_padding_on_sheet(graded_sheet)  # trim off padding so it aligns with printed one
        graded_sheet.save(file_path, "JPEG")

def convert_graded_to_pdf(username, quiz_name):
    quiz_dir = io.quiz_loc(username, quiz_name)
    dir_path = path.join(quiz_dir, 'sheets-graded', 'graded-overlays')
    sheet_count = get_sheet_count(username, quiz_name)
    img_paths = []
    for sheet_no in range(sheet_count):
        file_name = 'graded-overlay-' + str(sheet_no) + '.jpeg'
        img_paths.append(file_name)

    cmd = ['img2pdf', '--output', 'graded-overlays.pdf']
    cmd.extend(img_paths)
    subprocess.call(cmd, cwd=dir_path)
    
    cmd = ['img2pdf', '--output', 'graded-overlays-reversed.pdf']
    cmd.extend(reversed(img_paths))
    subprocess.call(cmd, cwd=dir_path)
    
    
    dir_path = path.join(quiz_dir, 'sheets-graded', 'graded-sheets')
    sheet_count = get_sheet_count(username, quiz_name)
    img_paths = []
    for sheet_no in range(sheet_count):
        file_name = 'graded-sheet-' + str(sheet_no) + '.jpeg'
        img_paths.append(file_name)

    cmd = ['img2pdf', '--output', 'graded-sheets.pdf']
    cmd.extend(img_paths)
    subprocess.call(cmd, cwd=dir_path)
    
