from quizitemfinder.io import quiz_loc, sheet_loc, count_sheets, open_sheet_im, open_sheet_img, save_item_im, save_header_im, find_sheet_dims, write_cv_data, create_quiz_directory_structure, save_rects, save_error_sheet_img, save_error_corrected_sheet_img, open_rects
from quizitemfinder.mark_squares import find_items_in_sheet_im, crop_out_item

from quizitemfinder.image_manipulation import paste_rects_on_sheet

# do all and handle errors
#COL_COUNT = 5
#ROW_COUNT = 10
#ITEM_COUNT = COL_COUNT * ROW_COUNT
#HEADER_COUNT = 3
#SHEET_COUNT = 21

# return true if no errors
#def check_items_for_error_free(items, header_count, item_count):
#    if(len(items["headers"]) is header_count and len(items["items"]) is item_count ):
#        return True
#    else:
#        return False




# sheet 0 is the blank sheet, so we can get the template from that sheet
# we can check the other sheets against this for errors
def default_items(username, quiz_name, sheet_no=0):
    sheet_im = open_sheet_im(username, quiz_name, sheet_no)
    items = find_items_in_sheet_im(sheet_im)
    return items
    
# correct items here, or reject them all if the errors cannot be resolved
def items_in_sheet_with_error_check(username, quiz_name, sheet_no, defaults):
    item_count = len(defaults["items"])
    header_count = len(defaults["headers"])
    sheet_im = open_sheet_im(username, quiz_name, sheet_no)
    items = find_items_in_sheet_im(sheet_im)
    # filter out unlikely rects
    if(len(items["items"]) is item_count ): # only check for item count, since we can worry about headers elsewhere
        return items
    else:
        return False

    
    
def save_items_and_headers_for_all_items(username, quiz_name):
    defaults = default_items(username, quiz_name)
    sheet_count = count_sheets(username, quiz_name)
    sheet_nos_for_errors = []
    rects = [None]*sheet_count
    for sheet_no in range(sheet_count):
        sheet_im = open_sheet_im(username, quiz_name, sheet_no)
        items = items_in_sheet_with_error_check(username, quiz_name, sheet_no, defaults)
        rects[sheet_no] = items
        if(items):
            # crop and save items
            for item_no, rect in enumerate(items["items"]):
                item_im = crop_out_item(sheet_im, rect)
                save_item_im(item_im, username, quiz_name, item_no, sheet_no)
            for header_no, rect in enumerate(items["headers"]):
                header_im = crop_out_item(sheet_im, rect)
                save_header_im(header_im, username, quiz_name, header_no, sheet_no)
        else:
            # TODO: add to errors
            # crop the defaults
            print('error on {}'.format(sheet_no))
            sheet_nos_for_errors.append(sheet_no)
            for item_no, rect in enumerate(defaults["items"]):
                item_im = crop_out_item(sheet_im, rect)
                save_item_im(item_im, username, quiz_name, item_no, sheet_no) 
            for header_no, rect in enumerate(defaults["headers"]):
                header_im = crop_out_item(sheet_im, rect)
                save_header_im(header_im, username, quiz_name, header_no, sheet_no)
    save_rects(username, quiz_name, rects)
    return sheet_nos_for_errors
    

    
def generate_quiz_metadata(username, quiz_name, sheets_with_errors):
    sheet_count    = count_sheets(username, quiz_name)
    sheet_dim      = find_sheet_dims(username, quiz_name, sheet_no=0)
    defaults = default_items(username, quiz_name)
    item_count = len(defaults["items"])
    # flatten the bounding_box
    bounding_boxes = [box[0] + box[1] for box in defaults["items"]] 
    header_bounding_boxes = [box[0] + box[1] for box in defaults["headers"]] 
    #item_count     = do_item_count_on_sheet(quiz_name, sheet_no=0, data_path=data_path)
    #bounding_boxes = find_bounding_boxes_for_sheet(quiz_name, sheet_no=0,data_path=data_path)
    #sheets_urls = [
    #    sheet_loc(quiz_name, sheet_no, data_path=data_path)
    #    for sheet_no in range(sheet_count)
    #]
    
    #digits_urls = [[
    #    {
    #        'item_src': item_path(sheet_no, item_no, quiz_name, data_path="./data/processed-quizzes/"),
    #        'digit_src': letter_path(sheet_no, item_no, quiz_name, data_path="./data/processed-quizzes/")
    #    }
    #    
    #    for item_no in range(item_count)
    #] for sheet_no in range(sheet_count)]
    
    return {
        #'sheets': sheets_urls,
        'code': quiz_name,
        'item_count': item_count,
        'sheet_count': sheet_count,
        #'digits': digits_urls,
        'source': 'v0',
        'bounding_boxes': bounding_boxes,
        'header_boxes': header_bounding_boxes,
        'corrections': [],
        "sheet_count": sheet_count,
        "sheet_dim": sheet_dim,
        "sheets_with_errors": sheets_with_errors
    }

def save_quiz_data_files(username, quiz_name, answer_key, sheets_with_errors=[]):
    create_quiz_directory_structure(username, quiz_name)
    cv_data = generate_quiz_metadata(username, quiz_name, sheets_with_errors)
    defaults = default_items(username, quiz_name)
    sheet_count = count_sheets(username, quiz_name)
    item_count = len(defaults["items"])
    corrections = [['', ''] + [1 for i in range(item_count)] for s in range(sheet_count)]
    write_cv_data(username, quiz_name, cv_data, answer_key, corrections)
    
from quizitemfinder.process_pdf import rawpdf2imgs, rename_sheets
def do_process_quiz(username, quiz_name, answer_key):
    rawpdf2imgs(username, quiz_name)
    rename_sheets(username, quiz_name)
    # answer_key = " ".join(["B A D D A",  "C B B C B"]).split(" ")
    sheets_with_errors = save_items_and_headers_for_all_items(username, quiz_name)
    save_quiz_data_files(username, quiz_name, 
                         answer_key=answer_key, 
                         sheets_with_errors=sheets_with_errors)
    # save error sheets
    error_imgs = []
    corrected_imgs = []
    default_rects = open_rects(username, quiz_name)[0]
    for sheet_no in sheets_with_errors:
        sheet_im = open_sheet_im(username, quiz_name, sheet_no)
        sheet_img = open_sheet_img(username, quiz_name, sheet_no)
        error_rects = find_items_in_sheet_im(sheet_im)
        error_img = paste_rects_on_sheet(sheet_img, error_rects)
        error_imgs.append([error_img, sheet_no])
        corrected_img = paste_rects_on_sheet(sheet_img, default_rects)
        corrected_imgs.append([corrected_img, sheet_no])
    for error_img, sheet_no in error_imgs:
        save_error_sheet_img(error_img, username, quiz_name, sheet_no)
    for corrected_img, sheet_no in corrected_imgs:
        save_error_corrected_sheet_img(corrected_img, username, quiz_name, sheet_no)

    
    return {"errors": sheets_with_errors}
    

