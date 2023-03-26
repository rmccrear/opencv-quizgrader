import cv2
import numpy as np
import matplotlib.pyplot as plt
from os import path, chdir, getcwd
    
import quizitemfinder.steps.utils as utils
#from quizitemfinder.steps.step1findcells import CellFinder, rectdims
#from quizitemfinder.steps.step1findcells import Demo as CellFinderDemo

from quizitemfinder.mark_squares import find_bounds_of_rects, is_rect_within_bounds


# floods the image
def fill_it(im, xy, modify_orig=False, color=0):
    im_floodfill = None
    if(modify_orig): im_floodfill = im
    else: im_floodfill = im.copy()
    h, w = im_floodfill.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    pix = cv2.floodFill(im_floodfill, mask, xy, color);
    #show_im(im_floodfill)
    return pix

# make it easy to find the squares with our data
def remove_bg(im, debug=False):
    blurred_im = cv2.GaussianBlur(im, ksize=(11,11),sigmaX=1)
    th, im_th = cv2.threshold(blurred_im, 220, 255, cv2.THRESH_BINARY_INV);
    ## This make the bottom of the box lower and includes the lower outline (not good)
    ## reversed_im = 255-blurred_im
    ## img_eroded = cv2.erode(reversed_im, kernel=(2,2), iterations=3)
    ## img_dilation = cv2.dilate(img_eroded, kernel=(2,2), iterations=1)
    ## img_dilated_eroded = img_dilation
    
    ### one dilation gets rid of the ouline well.
    img_dilation = cv2.dilate(im_th, kernel=(2,2), iterations=3)
    img_dilated_eroded = img_dilation
    
    #### Try dilate then erode. Less white color, then more. 
    #### reversed_im = 255-blurred_im
    #### img_dilation = cv2.dilate(reversed_im, kernel=(2,2), iterations=3)
    #### img_eroded = cv2.erode(img_dilation, kernel=(2,2), iterations=5)
    #### img_dilated_eroded = img_eroded
    
    # th, im_th = cv2.threshold(255-img_dilated_eroded, 220, 255, cv2.THRESH_BINARY_INV);
    # filled_im = im_th.copy()
    filled_im = img_dilated_eroded.copy()
    fill_it(filled_im, (0,0), modify_orig=True, color=255)
    if debug is False:
        return filled_im
    else:
        # return (blurred_im, reversed_im, img_eroded, img_dilation, im_th, filled_im)
        return (blurred_im, im_th, img_dilation, filled_im)



# rectangles bounding 
def getContRect(cnt):
    x,y,w,h = cv2.boundingRect(cnt)
    #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    return ((x,y), (x+w, y+h))

# determine id of rect based on position
def center_of_rect(rect):
    top_x = rect[0][0]
    top_y = rect[0][1]
    x_ = int((rect[1][0]-rect[0][0])/2)
    y_ = int((rect[1][1]-rect[0][1])/2)
    return (top_x + x_, top_y + y_)

def point_is_in_rect(pnt, rect):
    x, y = pnt
    x_range = (rect[1][0], rect[0][0])
    y_range = (rect[1][1], rect[0][1])
    return x>x_range[1] and x<x_range[0] and y>y_range[1] and y<y_range[0]

def sheet_rects_from_contours(reference_sheet_rects, contours):
    rects_of_contours = [getContRect(cnt) for cnt in contours]
    # filter by size
    acceptable_bounds = find_bounds_of_rects(reference_sheet_rects) # upper and lower limits for size of a rect
    correct_sized_rects = [rect for rect in rects_of_contours if is_rect_within_bounds(rect, acceptable_bounds)]

    header_len = len(reference_sheet_rects['headers'])
    item_len = len(reference_sheet_rects['items'])

    # organize based on position
    # build data structure for sheet_rect
    sheet_rects = {'headers': [False]*header_len, 'items': [False]*item_len}
    ref_rects_for_check = []
    for no, rect in enumerate(reference_sheet_rects["headers"]):
        ref_rects_for_check.append((rect, 'headers', no))
    for no, rect in enumerate(reference_sheet_rects["items"]):
        ref_rects_for_check.append((rect, 'items', no))
    # populate data structure
    for sheet_rect in correct_sized_rects:
        for idx, (ref_rect, kind, no) in enumerate(ref_rects_for_check):
            sheet_rect_center = center_of_rect(sheet_rect)
            if point_is_in_rect(sheet_rect_center, ref_rect):
                sheet_rects[kind][no]=sheet_rect
                #ref_rects_for_check.remove(idx)
                break
    return sheet_rects
    


# rectangles bounding 
def getContRect(cnt):
    x,y,w,h = cv2.boundingRect(cnt)
    #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    return ((x,y), (x+w, y+h))

# rects_of_contours = [getContRect(cnt) for cnt in contours]

def find_rects_from_im(sheet_im, reference_sheet_rects, debug=False):
    shape_mask = remove_bg(sheet_im)

    cnts = cv2.findContours(255-shape_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if(cv2.__version__.split('.')[0] != '3'):
        cnts = ['', cnts[0], cnts[1]] # cv2 4.0 lost the first return arg
    _, contours, _ =  cnts

    sheet_rects = sheet_rects_from_contours(reference_sheet_rects, contours)
    return sheet_rects

def fix_sheet_errors(sheet_rects, quiz_ref):
    reference_sheet_rects = sheet_rects[0]
    error_sheet_ids = [sheet_id for sheet_id, rects in enumerate(sheet_rects) if not rects]
    error_rects = [find_rects_from_im(quiz_ref.sheet_im(sheet_id), reference_sheet_rects) for sheet_id in error_sheet_ids]
    fixed_rectangles_for_cells_raw = [rects for rects in sheet_rects]
    for i in range(len(error_sheet_ids)):
        idx = error_sheet_ids[i]
        rect = error_rects[i]
        fixed_rectangles_for_cells_raw[idx] = rect
    return fixed_rectangles_for_cells_raw

