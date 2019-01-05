import cv2
import quizitemfinder.steps.utils as utils
from quizitemfinder.find_letters import find_letter_in_answer_box
import numpy as np



def enhance_item_im(img, kernel_size=(1,1), iters=1):
            im = img.copy()
            blurred_im = cv2.GaussianBlur(im, ksize=(11,11),sigmaX=1);
            img_dilation = blurred_im
            if iters > 0:
                kernel = np.ones(kernel_size, np.uint8)
                img_dilation = cv2.dilate(255-blurred_im, kernel, iterations=iters)
            # weird: why does this threshold fn seem to not invert the image?
            th, im_th = cv2.threshold(255-img_dilation, 220, 255, cv2.THRESH_BINARY_INV)
            return im_th

def im_with_lower_threshold(im, th):
    th_im = (im > th)*1     # this makes a binary b/w image 1/0
    # th_im = (im > th)*255  # this makes a binary image in  gray scale
    # th_im = (im > th)*im  # this makes a gray scale image with 
                             #lower lighter pixels removed
    return th_im

def normalize_letter(letter):
            # add padding 24x24 plus 2 padding (28x28)
            letter_im = (255 - cv2.resize(letter, (24, 24), interpolation=cv2.INTER_AREA))
            letter_im = cv2.copyMakeBorder(letter_im,2,2,2,2,cv2.BORDER_CONSTANT,value=0)
            # set lower threshold to 50 in array
            letter_im = im_with_lower_threshold(letter_im, 50)
            return letter_im

# todo: determince acceptable letter size based on answer key
def check_letter_cc_im(letter_cc_im):
    if len(letter_cc_im)<10: # just a dot
        return {"ERROR": "Letter Mark Too Small."}
    else:
        return "OK"

def letter_from_cell(cell_im):
        boxxes = find_letter_in_answer_box(enhance_item_im(cell_im))
        if len(boxxes) > 0:
            rect = boxxes[0]
            letter_cc_im = utils.croprect(cell_im, rect)
            check = check_letter_cc_im(letter_cc_im)
            if check != "OK":
                return check
            else:
                return normalize_letter(letter_cc_im)
        else:
            return {"ERROR": "No contours found in cell."}
            #return cell_im


class LetterCropper:
    def __init__(self):
        self.letter_from_cell = letter_from_cell

    def find_letters_from_rects_2d(self, cell_rects_for_sheets, sheet_images):
        letters = []
        # import pdb; pdb.set_trace()
        for rects_in_sheet, sheet_im in \
                zip(cell_rects_for_sheets, sheet_images):
            letters_for_sheet = []
            letter = None
            for cell_rect in rects_in_sheet:
                if "ERROR" not in cell_rect:
                    cell_im = utils.croprect(sheet_im, cell_rect)
                    letter_im = self.letter_from_cell(cell_im)
                    # TODO: check for new errors here
                    letter = letter_im
                else:
                    letter = cell_rect # return ERROR with message
                letters_for_sheet.append(letter)
            letters.append(letters_for_sheet)
        return letters

