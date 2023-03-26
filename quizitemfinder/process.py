from quizgrader2.io import open_sheet_im, save_item, save_letter, count_sheets, \
save_header_im, sheet_loc, item_path, header_im_path, letter_path

from quizgrader2.mark_squares import show_items_on_sheet_im, show_im, my_flatten

from quizgrader2.find_letters import process_sheet

DATA_PATH="./data/processed-quizzes/"


def show_sheet(quiz_name, sheet_no, data_path="./data/processed-quizzes/"):
    sheet_im = open_sheet_im(quiz_name, sheet_no=sheet_no, data_path=data_path)
    psheet = process_sheet(sheet_im)

    header_rects = psheet["rects"]["headers"]
    item_rects = psheet["rects"]["items"]
    #letter_rects = psheet["rects"]["letters"]

    show_im(show_items_on_sheet_im(sheet_im, header_rects))
    show_im(show_items_on_sheet_im(sheet_im, item_rects))
    for item_im in psheet["imgs"]["items"]:
        show_im(item_im)


def save_sheet_items(quiz_name, sheet_no, psheet, data_path="./data/processed-quizzes/"):
    header_imgs = psheet["imgs"]["headers"]
    item_imgs   = psheet["imgs"]["items"]
    letter_imgs = psheet["imgs"]["letters"]
    for h in range(len(header_imgs)):
        save_header_im(header_imgs[h], header_no=h, sheet_no=sheet_no, quiz_name=quiz_name, data_path=data_path)
        
    for i in range(len(item_imgs)):
        save_item(item_imgs[i], item_no=i, sheet_no=sheet_no, quiz_name=quiz_name, data_path=data_path)
        
    for l in range(len(letter_imgs)):
        save_letter(letter_imgs[l], item_no=l, sheet_no=sheet_no, quiz_name=quiz_name, data_path=data_path)
        
def open_process_and_save_sheet(quiz_name, sheet_no, data_path="./data/processed-quizzes/"):
    sheet_im = open_sheet_im(quiz_name, sheet_no, data_path=data_path)
    psheet = process_sheet(sheet_im)
    save_sheet_items(quiz_name, sheet_no, psheet, data_path=data_path)
    return psheet

def do_item_count_on_sheet(quiz_name, sheet_no, data_path="./data/processed-quizzes/"):
    sheet_im = open_sheet_im(quiz_name, sheet_no, data_path=data_path)
    psheet = process_sheet(sheet_im)
    return len(psheet["imgs"]["items"])

def find_sheet_dims(quiz_name, sheet_no, data_path="./data/processed-quizzes/"):
    sheet_im = open_sheet_im(quiz_name, sheet_no, data_path=data_path)
    SHEET_WIDTH = sheet_im.shape[1]; SHEET_HEIGHT=sheet_im.shape[0];
    return {'width': SHEET_WIDTH, 'height': SHEET_HEIGHT}

def find_bounding_boxes_for_sheet(quiz_name, sheet_no, data_path="./data/processed-quizzes/"):
    OFFSET_FOR_NUMBER = 17
    sheet_im = open_sheet_im(quiz_name, sheet_no, data_path=data_path)
    psheet = process_sheet(sheet_im)
    bbs = [my_flatten(rect) for rect in psheet["rects"]["items"]]
    for b in bbs:
        b[0] = b[0] + OFFSET_FOR_NUMBER
    return bbs



def process_quiz(quiz_name, data_path="./data/processed-quizzes/"):
    sheets_count = count_sheets(quiz_name, data_path=data_path)
    for sheet_no in range(sheet_count):
        psheet = open_process_and_save_sheet(quiz_name, sheet_no, data_path=data_path)
    return {
        sheet_count: sheets_count
    }
     


def process_quiz(quiz_name, data_path="./data/processed-quizzes/"):
    sheet_count = count_sheets(quiz_name, data_path=data_path)
    item_count = do_item_count_on_sheet(quiz_name, 0, data_path=data_path)
    sheet_nos_with_errors = []
    
    for sheet_no in range(sheet_count):
        psheet = open_process_and_save_sheet(quiz_name, sheet_no, data_path=data_path)
        if(len(psheet["imgs"]["items"]) < item_count):
            print("error in sheet_no: {}, only {} out of {} items found".format(sheet_no, len(psheet["imgs"]["items"]), item_count))
            sheet_nos_with_errors.append(sheet_no)
    return {
        "sheet_count": sheet_count,
        "sheets_with_errors": sheet_nos_with_errors
    }



def generate_quiz_metadata(quiz_name, answer_key, data_path="./data/processed-quizzes/"):
    sheet_count    = count_sheets(quiz_name, data_path=data_path)
    sheet_dim      = find_sheet_dims(quiz_name, sheet_no=0,data_path=data_path)
    item_count     = do_item_count_on_sheet(quiz_name, sheet_no=0, data_path=data_path)
    bounding_boxes = find_bounding_boxes_for_sheet(quiz_name, sheet_no=0,data_path=data_path)
    sheets_urls = [
        sheet_loc(quiz_name, sheet_no, data_path=data_path)
        for sheet_no in range(sheet_count)
    ]
    
    digits_urls = [[
        {
            'item_src': item_path(sheet_no, item_no, quiz_name, data_path="./data/processed-quizzes/"),
            'digit_src': letter_path(sheet_no, item_no, quiz_name, data_path="./data/processed-quizzes/")
        }
        
        for item_no in range(item_count)
    ] for sheet_no in range(sheet_count)]
    
    return {
        'sheets': sheets_urls,
        'code': quiz_name,
        'item_count': item_count,
        'sheet_count': sheet_count,
        'digits': digits_urls,
        'source': 'v0',
        'bounding_boxes': bounding_boxes,
        'corrections': [],
        "sheet_count": sheet_count,
        "sheet_dim": sheet_dim
    }






#
# for errors
#
def process_sheet_with_default_rects(quiz_name, sheet_no, data_path=DATA_PATH):
    blank_sheet_im = open_sheet_im(quiz_name, sheet_no=0, data_path=data_path)
    default_psheet = process_sheet(blank_sheet_im)

    sheet_im = open_sheet_im(quiz_name, sheet_no=sheet_no, data_path=data_path)
    psheet = process_sheet(sheet_im, default_psheet["rects"])
    return psheet

# def check_psheet(quiz_name, sheet_no, data_path=DATA_PATH):

def process_and_save_sheet_with_default_rects(quiz_name, sheet_no, data_path=DATA_PATH):
    psheet = process_sheet_with_default_rects(quiz_name, sheet_no=sheet_no, data_path=data_path)
    return save_sheet_items(quiz_name, sheet_no=sheet_no, psheet=psheet, data_path=data_path)

