#from quizgrader2.mark_squares import getContRect, sort_row_by_horz, find_rects_in_img, organize_found_items, crop_out_item, enhance_item_im, filter_conts_area
from quizitemfinder.mark_squares import getContRect, sort_row_by_horz, find_rects_in_img, organize_found_items, crop_out_item, enhance_item_im, filter_conts_area
import cv2
import numpy as np




def find_conts_in_answer_box(item_im):
    cnts = cv2.findContours(item_im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if(cv2.__version__.split('.')[0] != '3'):
        cnts = ['', cnts[0], cnts[1]] # cv2 4.0 lost the first return arg
    return cnts[1]


# input:   enhanced image
# returns: rectagle of letter [((,),(,))]
# gets rightmost box of area 30 or larger
def find_letter_in_answer_box(item_im):
    conts = find_conts_in_answer_box(item_im)
    larger_conts = filter_conts_area(conts, min_area=30)
    lg_rects = [getContRect(c) for c in larger_conts]
    if len((lg_rects)):
       sort_row_by_horz(lg_rects)
       rightmost = [lg_rects[-1]]
       return rightmost
    else:
       return []

#input b/w crop from sheet image
#output image of cropped enhanced letter
def process_letter(item_im):
    enhanced_item_im = enhance_item_im(item_im, kernel_size=(2,2), iters=1)
    letter_rect = find_letter_in_answer_box(enhanced_item_im)
    rects_en_im = show_rects_in_img(enhanced_item_im, letter_rect, width=1) 
    return rects_en_im


def normalize_letter_im(letter_im, size=(26,26)):
    im = letter_im
    th, im = cv2.threshold(255-im, 50, 255, cv2.THRESH_BINARY_INV);
    im = cv2.resize(im, (size[1]-2, size[0]-2), interpolation=cv2.INTER_AREA)
    th, im = cv2.threshold(255-im, 50, 255, cv2.THRESH_BINARY_INV);
    #resized_im = cv2.resize(letter_im, (size[1]-2, size[0]-2), interpolation=cv2.INTER_AREA)
    #th, im_th = cv2.threshold(255-resized_im, 50, 255, cv2.THRESH_BINARY_INV);
    #padded_im = np.pad(im_th, (2,2), mode='constant', constant_values=(255, 255))
    ###imm = deskew(padded_im)
    ###show_im(imm)
    #return 255-padded_im
    # im = im_th
    return 255 - im


#input b/w crop from sheet image
#output image of cropped enhanced letter
def process_letter(enhanced_item_im, item_im):
    #enhanced_item_im = enhance_item_im(item_im, kernel_size=(2,2), iters=1)
    #letter_rect = find_letter_in_answer_box(enhanced_item_im)
    letter_rect = find_letter_in_answer_box(enhanced_item_im)
    if(len(letter_rect) > 0):
        letter_im = crop_out_item(item_im, letter_rect[0])
        return (letter_im, letter_rect)
    else:
        print("error can't find letter in answer box")
        return (None, None)




# input b/w sheet image
# output: rects
def process_items(sheet_im):
    rects = find_rects_in_img(sheet_im, kernel_size=(2,2), iters=1)
    # rects = find_rects_in_img(sheet_im, kernel_size=(1,1), iters=0)
    # print(rects)
    if(len(rects) == 0):
        return {
                  "headers": [],
                  "items": []
               }
    else:
        items = organize_found_items(rects)
        return items

# input b/w sheet image, rects to crop
# output: cropped images of the sheet
def crop_items(sheet_im, rects):
    #rects = process_items(sheet_im)
    return {
        "headers": [crop_out_item(sheet_im, r) for r in rects["headers"]],
        "items":   [crop_out_item(sheet_im, r) for r in rects[ "items" ]]
    }
    

def process_sheet(sheet_im, item_rects_default=None):
    item_rects = process_items(sheet_im)
    if(item_rects_default != None):
        item_rects = item_rects_default
        #print('using defaults for processing sheet')
        #item_rects["items"] = item_rects_default
        #print(len(item_rects["items"]))
    images = crop_items(sheet_im, item_rects)
    enhanced_item_images = [enhance_item_im(item_im, kernel_size=(2,2), iters=1) for item_im in images["items"]]
    en_reg_items = zip(images["items"], enhanced_item_images)
    letters = [process_letter(en_im, im) for im, en_im in en_reg_items]
    letter_images = [l[0] for l in letters]
    for idx, l_im in enumerate(letter_images):
        if l_im == None:
            print("error on letter no: " + str(idx))
    letter_images = [normalize_letter_im(im) for im in letter_images]
    #letter_rects = [[l[1]] for l in letters]
    #letter_rects = put_letter_rects_in_sheet(item_rects["items"], letter_rects)
    return {
        "imgs": {
            "headers": images["headers"],
            "items":   images["items"],
            "letters": letter_images
        },
        "rects": {
            "headers": item_rects["headers"],
            "items":   item_rects["items"]#,
        #    "letters": letter_rects
        }
    }


# This is like pro
#from quizgrader2.io import open_sheet_im
from quizitemfinder.io import open_sheet_im
def process_sheet_with_default_bounding_box(quiz_name, sheet_no, data_path="./data/processed-quizzes/"):
    #get_defaults
    blank_sheet_im = open_sheet_im(quiz_name, 0, data_path=data_path)
    #blank_psheet=process_sheet(blank_sheet_im)
    blank_items = process_items(blank_sheet_im)
    #default_item_rects = blank_psheet["rects"]["items"]
    print("defaults")
    print(len(default_item_rects))
    sheet_im = open_sheet_im(quiz_name, sheet_no, data_path=data_path)
    #psheet = process_sheet(sheet_im, item_rects_default=default_item_rects)
    psheet = process_sheet(sheet_im, item_rects_default=blank_items)
    return psheet


## Use like so...
#sheet_im = open_sheet_im("5NSC1-Midterm", sheet_no=5, data_path=TEST_DATA_PATH)
#psheet = process_sheet(sheet_im)
#
#header_rects = psheet["rects"]["headers"]
#item_rects = psheet["rects"]["items"]
##letter_rects = psheet["rects"]["letters"]
#
#sheet_with_rects_im = show_items_on_sheet_im(sheet_im, sheet_rects["items"])
#
#show_im(show_items_on_sheet_im(sheet_im, header_rects))
#show_im(show_items_on_sheet_im(sheet_im, item_rects))
##show_im(show_items_on_sheet_im(sheet_im, letter_rects))
#
#
#for letter_im in psheet["imgs"]["letters"]:
#    show_im(letter_im)
