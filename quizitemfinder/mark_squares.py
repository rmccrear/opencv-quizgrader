from PIL import Image, ImageDraw
import cv2
from matplotlib import pyplot as plt
import numpy as np
import functools
import json
import glob

from quizitemfinder.shape_detector import bounding_rectangles_for_rectangular_shapes

#weirdness coming from adding kernel_size and iters options.
# not sure which is flowing down to the bottom fns


def show_im(im, interpolation='nearest'):
    plt.imshow(im, cmap = 'gray', interpolation=interpolation, aspect='auto')
    plt.xticks([]), plt.yticks([])
    plt.show()
    
def enhance_sheet(img, kernel_size=(2,2), iters=1):
    im = img.copy()
    blurred_im = cv2.GaussianBlur(im, ksize=(11,11),sigmaX=1);
    #show_im(blurred_im)
    img_dilation = None #blurred_im
    if iters > 0:
        kernel = np.ones(kernel_size, np.uint8)
        img_dilation = cv2.dilate(255-blurred_im, kernel, iterations=iters)
    else:
        img_eroded = cv2.erode(255-blurred_im, kernel_size, iterations=2)
        img_dilation = cv2.dilate(img_eroded, kernel_size, iterations=2)
        #img_dilation=255-blurred_im
    #show_im(img_dilation)
    # weird: why does this threshold fn seem to not invert the image?
    th, im_th = cv2.threshold(255-img_dilation, 220, 255, cv2.THRESH_BINARY_INV);
    #show_im(im_th)
    # Copy the thresholded image.
    #im_floodfill = im_th.copy()
    return im_th

def fill_it(im, xy, modify_orig=False, color=0):
    im_floodfill = None
    if(modify_orig): im_floodfill = im
    else: im_floodfill = im.copy()
    h, w = im_floodfill.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    pix = cv2.floodFill(im_floodfill, mask, xy, color);
    #show_im(im_floodfill)
    return pix



def findConts(shapeMask):
    # find the contours in the mask
    cnts = cv2.findContours(255-shapeMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #print("I found {} black shapes".format(len(cnts[1])))
    return cnts

    # loop over the contours
    #for c in cnts:
        # draw the contour and show it
def draw_conts_in_color(im, conts, color=(255,0,0), width=2):
    backtorgb = cv2.cvtColor(im.copy(),cv2.COLOR_GRAY2RGB)
    cv2.drawContours(backtorgb, conts, -1, color, width)
    return backtorgb

def filter_conts_area(conts, min_area=1000):
    large_conts = []
    for c in conts:
        if(cv2.contourArea(c) >= min_area): 
            large_conts.append(c)
    return large_conts



def getContRect(cnt):
    x,y,w,h = cv2.boundingRect(cnt)
    #cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
    return ((x,y), (x+w, y+h))


def show_rects_in_img(blank_sheet_im, rects, color=(0,255,0), width=2):
    rect_im = cv2.cvtColor(blank_sheet_im.copy(),cv2.COLOR_GRAY2RGB)
    for rect in rects:
        cv2.rectangle(rect_im, rect[0], rect[1], (0,255,0), width)
    #print("I found {} large rectangles".format(len(rects)))
    #show_im(rect_im, interpolation="gaussian")
    return rect_im
    

def find_rects_in_img(blank_sheet_im, kernel_size=(2,2), iters=1, min_area=1000):

    enhanced_sheet = enhance_sheet(blank_sheet_im, kernel_size=kernel_size, iters=iters)
    #show_im(enhanced_sheet)
    ##show_im(blank_sheet_im)
    filled_im = enhanced_sheet.copy()
    fill_it(filled_im, (0,0), modify_orig=True, color=255)
    #show_im(filled_im)
    inv_squares_im = 255-filled_im
    #show_im(inv_squares_im)
    cnts = findConts(filled_im)

    #conts_im = draw_conts_in_color(blank_sheet_im.copy(), cnts[1])
    #show_im(conts_im)

    large_conts = filter_conts_area(cnts[1], min_area=min_area)
    #conts_large_im = draw_conts_in_color(blank_sheet_im.copy(), large_conts)
    #print("I found {} large black shapes".format(len(large_conts)))
    #show_im(conts_large_im)

    rects = [getContRect(c) for c in large_conts]
    return rects


def find_conts_for_im(blank_sheet_im):
    enhanced_sheet = enhance_sheet(blank_sheet_im, kernel_size=(2,2), iters=1)
    filled_im = enhanced_sheet.copy()
    fill_it(filled_im, (0,0), modify_orig=True, color=255)
    inv_squares_im = 255-filled_im
    cnts = findConts(filled_im)
    return cnts



# sort by top-left corner pos.
# with d= acceptable range in pix for rows

def vert_of(item):
    top_corner, bottom_corner = item
    x1, y1 = top_corner
    x2, y2 = bottom_corner
    return y1

def horz_of(item):
    top_corner, bottom_corner = item
    x1, y1 = top_corner
    x2, y2 = bottom_corner
    return x1

def is_in_row(vert_pos, item, d):
    top_corner, bottom_corner = item
    x1, y1 = top_corner
    x2, y2 = bottom_corner
    if abs(vert_pos-y1) < 10:
        return True
    else:
        return False

def put_into_row(item, rows, d):
        row_keys = rows.keys()
        the_rows_k = None
        for k in row_keys:
            if is_in_row(k, item, d):
                the_rows_k = k
        if the_rows_k != None:
            rows[the_rows_k].append(item)
        else:
            rows[vert_of(item)] = [ item ]
            
def put_into_rows(items, d=10):
    rows = {}
    for item in items:
        put_into_row(item, rows, d)
    return list(rows.values())

#just take vert position of first item in list
def sort_rows_by_vert_key(items):
    return vert_of(items[0])
    
def sort_rows_by_vert(rows):
    rows.sort(key=sort_rows_by_vert_key)

def sort_row_by_horz(row, d=10):
    row.sort(key=horz_of)
    
def sort_rows_by_horz(rows, d=10):
    for i in range(len(rows)):
        sort_row_by_horz(rows[i])
        
def my_flatten(list_of_lists):
    z = list_of_lists
    return list( (x for y in z for x in y) )

def organize_found_items(items, header_rows=1, header_len=3, row_len=5, d=10):
    rows = put_into_rows(items, d=d)
    sort_rows_by_vert(rows)
    sort_rows_by_horz(rows, d=d)
    # some heuristics for skipping headers if none found
    # since somtimes the headers are filled up by the name and hard
    # to detect.
    # for example if the writing is too thick prevents us from finding
    # the boxes
    if(row_len>header_len and len(rows[0])<row_len):
        # we proceed normally
        return {
            'headers': my_flatten(rows[:header_rows]),
            'items': my_flatten(rows[header_rows:])
        }
    else:
        print("missing headers row_len: {}, header_len: {}, rows[0]: {}".format(row_len, header_len, len(rows[0])))
        # we are missing headers
        return {
            'headers': my_flatten(rows[:header_rows]),
            'items': my_flatten(rows)
        }
    

def area_of_rect(rect):
    # rect = ((x,y), (x+w, y+h))
    #return (rect[1][0]-rect[0][0]) * (rect[1][1]-rect[0][1])
    return height_of_rect(rect) * width_of_rect(rect)
def height_of_rect(rect):
    # rect = ((x,y), (x+w, y+h))
    return (rect[1][1]-rect[0][1])
def width_of_rect(rect):
    # rect = ((x,y), (x+w, y+h))
    return (rect[1][0]-rect[0][0])

def find_min_max_of_rects(ref_rects):
    all_ref_rects = []
    all_ref_rects.extend(ref_rects["headers"])
    all_ref_rects.extend(ref_rects["items"])
    ref_rect_areas = [area_of_rect(rect) for rect in all_ref_rects]
    min_area = min(ref_rect_areas)
    max_area = max(ref_rect_areas)
    lower_bound = int(min_area - min_area*.9)
    upper_bound = int(max_area + max_area*.9)
    return (lower_bound, upper_bound)
from collections import namedtuple
RectBounds = namedtuple('RectBounds', ['min_width', 'max_width', 'min_height', 'max_height', 'min_area', 'max_area'])
RectDims = namedtuple('RectDims', ['width', 'height', 'area'])
def find_bounds_of_rects(ref_rects, acceptable_error=.1):
    #print(ref_rects)
    e = acceptable_error
    all_ref_rects = ref_rects["headers"] + ref_rects["items"]
    ref_rect_areas   = [area_of_rect(rect)   for rect in all_ref_rects]
    ref_rect_widths  = [width_of_rect(rect)  for rect in all_ref_rects]
    ref_rect_heights = [height_of_rect(rect) for rect in all_ref_rects]
    min_area = min(ref_rect_areas)
    max_area = max(ref_rect_areas)
    min_width = min(ref_rect_widths)
    max_width = max(ref_rect_widths)
    min_height = min(ref_rect_heights)
    max_height = max(ref_rect_heights)
    return RectBounds(
        min_width=int(min_width*(1-e)),
        max_width=int(max_width*(1+e)),
        min_height=int(min_height*(1-e)),
        max_height=int(max_height*(1+e)),
        min_area=int(min_area*(1-e)),
        max_area=int(max_area*(1+e))
    )
def find_dims_of_rect(rect):
    #print(rect)
    return RectDims(
        width=width_of_rect(rect),
        height=height_of_rect(rect),
        area=area_of_rect(rect)
    )
    
# heuristic to filter out bad rects
def is_rect_within_bounds(rect, bounds):
    dims = find_dims_of_rect(rect)
    #print(dims)
    if(dims.width>bounds.min_width   and dims.width<bounds.max_width and
       dims.height>bounds.min_height and dims.height<bounds.max_height and
       dims.area>bounds.min_area     and dims.area<bounds.max_area):
        return True
    else:
        return False
    
#def is_too_large_or_small(contour, bounds):
#    min_area, max_area = bounds
#    area = cv2.contourArea(c)
#    if(area<min_area or area >max_area):
#        return True
#    else
#        return False
#def filter_high_and_low(conts, bounds):
#    return [cont in conts if (not is_too_large_or_small(cont, bounds))]

def find_items_in_reference_im(sheet_im, kernel_size=(2,2), iters=1, header_rows=1, d=10, area_min_max=(1000, 100000)):
    _, conts, hierarchy = find_conts_for_im(sheet_im)
    all_rects = [getContRect(c) for c in conts]
    # are the conts rectangular?
    # remove non-rectangles
    #
    # are the rects the same size
    # find the 
    

def find_items_in_sheet_im_with_check(sheet_im, reference_rects):
    all_ref_rects = reference_rects['headers'] + reference_rects['items']
    bounds_of_ref = find_bounds_of_rects(reference_rects)
    print(bounds_of_ref)
    _, conts, hierarchy = find_conts_for_im(sheet_im)
    all_rects = [getContRect(c) for c in conts]
    good_rects = [rect for rect in all_rects if is_rect_within_bounds(rect, bounds_of_ref)]
    print(good_rects)
    return organize_found_items(good_rects, header_rows=1, d=10)

def bounding_rect_to_rect(bounding_rect):
    x,y,w,h = bounding_rect
    return ((x,y), (x+w, y+h))

def find_items_in_sheet_im(sheet_im, kernel_size=(2,2), iters=1, header_rows=1, d=10, area_min_max=(1000, 100000)):
    #rects = find_rects_in_img(sheet_im, kernel_size=kernel_size, iters=iters)
    _, conts, hierarchy = find_conts_for_im(sheet_im)
    #conts = find_conts_for_im(sheet_im)[1]
    bounding_rects = bounding_rectangles_for_rectangular_shapes(conts)
    rects = [bounding_rect_to_rect(c) for c in bounding_rects]
    #all_rects = [getContRect(c) for c in conts]
    #rects = [rect for rect in all_rects if area_of_rect(rect)>area_min_max[0] and area_of_rect(rect)<area_min_max[1]]
    return organize_found_items(rects, header_rows=1, d=10)
def show_items_on_sheet_im(sheet_im, rects):
    im = sheet_im.copy()
    return show_rects_in_img(im, rects)


# crops the answer blank 
# TODO: leftcrop opt to crop out the number?
def crop_out_item(sheet_im, item_rect):
    top_corner, bottom_corner = item_rect
    x1, y1 = top_corner
    x2, y2 = bottom_corner
    return sheet_im[y1:y2, x1:x2]




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


def crop_answer_from_item_blank(enhanced_item_im):
    conts = findConts(enhanced_item_im)
    return conts


#item = enhanced item image
def crop_answer_from_item_im(item, iters=1, min_area=15, kernel_size=(2,2)):
    rects = find_rects_in_img(item, min_area=min_area, iters=iters, kernel_size=kernel_size)
    sort_row_by_horz(rects)
    if(len(rects) > 0):
        rightmost = rects[-1]
        cropped_letter = crop_out_item(item, rightmost)
        return cropped_letter
    else:
        return item

# https://www.learnopencv.com/handwritten-digits-classification-an-opencv-c-python-tutorial/
# doesn't work
def deskew(img):
    SZ=3
    m = cv2.moments(img)
    if abs(m['mu02']) < 1e-2:
        # no deskewing needed. 
        return img.copy()
    # Calculate skew based on central momemts. 
    skew = m['mu11']/m['mu02']
    # Calculate affine transform to correct skewness. 
    M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
    # Apply affine transform
    img = cv2.warpAffine(img, M, (SZ, SZ), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
    return img

def normalize_letter_im(letter_im, size=(24,24)):
    resized_im = cv2.resize(letter_im, (size[1]-2, size[0]-2), interpolation=cv2.INTER_AREA)
    th, im_th = cv2.threshold(255-resized_im, 220, 255, cv2.THRESH_BINARY_INV);
    padded_im = np.pad(im_th, (2,2), mode='constant', constant_values=(0, 0))
    #imm = deskew(padded_im)
    #show_im(imm)
    return padded_im


def crop_items_for_sheet(sheet_im, sheet_rects):
    cropped_ims = []
    for item_rect in sheet_rects['items']:
        item = crop_out_item(sheet_im, item_rect)
        cropped_ims.append(item)
        #show_im(item) 
    return cropped_ims

def crop_letters_for_sheet(sheet_im, sheet_rects, iters=1, kernel_size=(2,2)):
    cropped_ims = []
    for item_rect in sheet_rects['items']:
        item = enhance_item_im(crop_out_item(sheet_im, item_rect))
        #show_im(crop_answer_from_item_im(item, iters=2))
        cropped_im = crop_answer_from_item_im(item, iters=iters, kernel_size=kernel_size)
        normalized_im = normalize_letter_im(cropped_im)
        cropped_ims.append(normalized_im)
    return cropped_ims
