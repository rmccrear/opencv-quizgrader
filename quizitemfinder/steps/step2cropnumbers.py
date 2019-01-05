import cv2
import quizitemfinder.io as io
from quizitemfinder.steps.utils import croprect as crop_out_item

# this makes closure for all the fns needed only for cropping out the digit
#def crop_out_numbering_for_quiz_fn():
def convert_xyhw_to_rect_pnts(xywh):
    x,y,w,h = xywh[0], xywh[1], xywh[2], xywh[3]
    return ((x, y), (x+w, y+w))

def find_countours_of_numbering(im):
    imgray = im # cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

# find numbering location OK
def bounding_rects_for_cc(cnts):
    return [cv2.boundingRect(c) for c in cnts]



# find width to crop OK
def left_of_rect(rect):
    r = convert_xyhw_to_rect_pnts(rect)
    return r[1][1]  # r == ((x, y), (x+w, y+w))
def leftmost_contour_limit(rects, max_left):
    leftmosts_limits = [left_of_rect(r) for r in rects]
    leftmosts_limits = [l for l in leftmosts_limits if l<max_left]
    return max(leftmosts_limits)
def find_leftmost_from_reference_cell(im):
    w = len(im[0])
    max_left = int(w/2)
    cc = find_countours_of_numbering(im)
    rects = bounding_rects_for_cc(cc)
    # print(rects)
    leftmost = leftmost_contour_limit(rects, max_left)
    return leftmost
# open image OK
# crop off number OK
# crop_cell_1 crop off numbers based on reference cell
#def crop_cell_1(quiz, sheet_no, item_no):
#    ref_im = open_ref_cell(quiz, item_no)
#    leftmost = find_leftmost_from_reference_cell(ref_im)
#    cell_im = open_cell_im(quiz, sheet_no, item_no)
#    return cell_im[:,leftmost:]


# this is the amount to crop off
def find_leftmost_of_digits_from_im(sheet_im, cell_rects):
    leftmosts = []
    for i, rect in enumerate(cell_rects["items"]):
        full_cell = crop_out_item(sheet_im, rect)
        leftmost = find_leftmost_from_reference_cell(full_cell)
        leftmosts.append(leftmost) 
    return leftmosts

def find_leftmost_of_digits(username, quiz_name):
    sheet_im = io.open_sheet_im(username, quiz_name, 0)
    rectangles_for_quiz = io.open_rects(username, quiz_name)
    rects = rectangles_for_quiz[0] # rectangles for reference sheet
    return find_leftmost_of_digits_from_im(sheet_im, rects)


def create_fn(username, quiz_name):
    leftmosts = find_leftmost_of_digits(username, quiz_name)
    def crop_out_digit_from_cell(cell_im, item_no):
        leftmost = leftmosts[item_no]
        return cell_im[:,leftmost:]
    return (crop_out_digit_from_cell, leftmosts)
    
crop_out_numbering_for_quiz_fn = create_fn

# todo:
#   def __init__(self, reference_sheet_im, reference_cell_rects):

class NumberCropper:
    def __init__(self, username, quiz_name):
        self.username, self.quiz_name = (username, quiz_name)
        self.crop_away_number, self.leftmosts=create_fn(username, quiz_name)

    def crop_rect(self, rect, item_no):
        leftmost = self.leftmosts[item_no]
        # deepcopy
        x0, y0 = rect[0]
        x1, y1 = rect[1]
        return ((x0+leftmost, y0), (x1, y1))
    def crop_rects_2d(self, rects2d):
        new_rects_2d=[]
        for rects in rects2d:
            new_rects = []
            for item_no, rect in enumerate(rects):
                if rect is not False:
                    new_rects.append(self.crop_rect(rect, item_no))
                else:
                    new_rects.append({"ERROR": "no rect found for cell"})
            new_rects_2d.append(new_rects)
        return new_rects_2d


