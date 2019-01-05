import cv2
import matplotlib.pyplot as plt
import quizitemfinder.io as io
import csv

def drawrect(im, rect):
    pnts = rect
    if(len(rect) == 4): 
        x, y, w, h = rect
        pnts = ((x, y), (x+w, y+h))
    return cv2.rectangle(im.copy(), tuple(pnts[0]), tuple(pnts[1]), 150, cv2.FILLED)

def croprect(im, rect):
    pnts = rect
    if(len(rect)==4):
        x, y, w, h = rect
        pnts = ((x, y), (x+w, y+h))
    top_corner, bottom_corner = rect
    x1, y1 = top_corner
    x2, y2 = bottom_corner
    return im[y1:y2, x1:x2]

def showim(im, title=None, cmap='gray'):
    if(title is not None):
        plt.title(title)
    plt.imshow(im, cmap=cmap, interpolation='gaussian');

class QuizRef:
    def __init__(self, username, quiz_name):
        self.username, self.quiz_name = (username, quiz_name)
        self.sheet_count = io.count_sheets(username, quiz_name)

    def sheet_im(self, sheet_no):
        return io.open_sheet_im(self.username, self.quiz_name, sheet_no)
    def get_sheet_images(self):
        return [
                self.sheet_im(sheet_no) \
                for sheet_no in range(self.sheet_count) \
               ]
    def __str__(self):
        return "<QuizRef: {}/{}>".format(self.username, self.quiz_name)
    def __repr__(self):
        return self.__str__()

    def get_answer_key(self):
        return io.get_answer_key(self.username, self.quiz_name)

    def get_corrections(self):
        return io.get_corrections(self.username, self.quiz_name)

    def get_item_count(self):
        self.item_count = io.get_item_count(self.username, self.quiz_name)
        return self.item_count

    def write_item_image_data_rows(self, rows):
        quiz_loc = io.quiz_loc(self.username, self.quiz_name)
        csv_loc = quiz_loc + 'image_data.csv'
        print(csv_loc)
        with open(csv_loc, "w") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

