import quizitemfinder.steps.utils as utils
from quizitemfinder.steps.step1findcells import CellFinder
from quizitemfinder.steps.step2cropnumbers import NumberCropper
from quizitemfinder.steps.step3findhandwrittenletter import LetterCropper
from quizitemfinder.steps.step4items import Items

import numpy as np

from glob import glob
import os
class ImageDataCollector:
    def __init__(self, for_prediction=False):
        self.for_prediction = for_prediction # don't load val
                                             # from answer_key
    
    def find_quiz_names(self, username):
        quiz_dirs = glob("./score_data/{}/processed_quizzes/*/".format(username))
        quiz_names = [path.rstrip("/").split("/")[-1] for path in quiz_dirs]
        return quiz_names
# step 1
    def step1(self, quiz_ref):
        self.quiz_ref = quiz_ref
        #self.quiz_ref = utils.QuizRef('rmcc', '107-2--4BH106--QUIZ-1')
        cell_finder = CellFinder(quiz_ref=quiz_ref)
        rectangles_for_cells_raw = cell_finder.find_cells()
        item_count = len(rectangles_for_cells_raw[0]["items"])
        def maybe_items(x):
            if x is not False: return x["items"]
            else:              return [False for i in range(item_count)]
        # just the items
        item_rects_in_quiz = [maybe_items(rects_for_sheets) for rects_for_sheets in rectangles_for_cells_raw]
        return item_rects_in_quiz
# step 2
    def step2(self, quiz_ref, item_rects_in_quiz):
        number_cropper = NumberCropper(quiz_ref.username, quiz_ref.quiz_name)
        cleaned_rects_for_quiz = number_cropper.crop_rects_2d(item_rects_in_quiz)
        return cleaned_rects_for_quiz
# step 3 input the images of cells and find the letters
    def step3(self, quiz_ref, cleaned_rects_for_quiz):
        sheet_images = quiz_ref.get_sheet_images()
        letter_cropper = LetterCropper()
        letter_images = letter_cropper.find_letters_from_rects_2d(cleaned_rects_for_quiz, sheet_images)
        return letter_images
# write to csv
    def step4(self, quiz_ref, letter_images):
        items = Items(quiz_ref, for_prediction=self.for_prediction)
        #import pdb; pdb.set_trace()
        items.load_letters_2d(letter_images)
        return items
    def process_a_quiz(self, username=None, quiz_name=None, quiz_ref=None):
        if quiz_ref is None:
            quiz_ref = utils.QuizRef(username, quiz_name)
        print("processing: {}".format(quiz_ref))
        s1 = self.step1(quiz_ref)
        s2 = self.step2(quiz_ref, s1)
        s3 = self.step3(quiz_ref, s2)
        items = self.step4(quiz_ref, s3)
        return items

    def process_all_quizzes(self, username, except_these=None):
        quiz_names = self.find_quiz_names(username)
        if except_these is not None:
            for name in except_these:
                quiz_names.remove(name)# exclude these quizzes

        for quiz_name in quiz_names:
            print("processing quiz: {}".format(quiz_name))
            items = self.process_a_quiz(username, quiz_name)
            items.write_to_csv()
        concat_image_data(quiz_names) # collect csv data into one file
        return quiz_names
    
    def process_a_sheet(self, quiz_ref, sheet_no):
        s1 = self.step1(quiz_ref)
        s2 = self.step2(quiz_ref, s1)
        s3 = self.step3(quiz_ref, s2)
        s4 = self.step4(quiz_ref, s3)
        return [item for item in s4.items if item.sheet_no == sheet_no]
        
def cat_file(origin, dest, start=1): #(skips header)
    i=0
    with open(dest, "a") as d:
        with open(origin, "r") as o:
            for line in o:
                if i>=start: d.write(line)
                else:        i=i+1 

def read_first_line(file_name):
    first_line = None
    with open(file_name, "r") as f:
        first_line = f.readline()
    return first_line

def concat_image_data(quiz_names):
    headers = read_first_line("./score_data/rmcc/processed_quizzes/{}/image_data.csv".format(quiz_names[0]))
    with open("./score_data/rmcc/processed_quizzes/image_data.csv", "w") as f:
        f.write(headers)
    for quiz_name in quiz_names:
        cat_file("./score_data/rmcc/processed_quizzes/{}/image_data.csv".format(quiz_name),
        "./score_data/rmcc/processed_quizzes/image_data.csv")

#idc = ImageDataCollector() 
#idc.process_all_quizzes("rmcc")
#idc.process_a_quiz("rmcc", "107-2--4BH106--QUIZ-1")
#idc.process_all_quizzes("rmcc")
