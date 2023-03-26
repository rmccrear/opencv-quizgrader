import quizitemfinder.steps.utils as utils
import numpy as np

class ItemImageData:
    def __init__(self, quiz_ref, sheet_no, item_no, val, letter_im):
        self.quiz_ref = quiz_ref
        self.sheet_no = sheet_no
        self.item_no = item_no
        self.val = val
        self.predicted_val = None
        self.score = None
        self.letter_im = letter_im
        self.has_error = letter_has_error(self.letter_im)
        self.error_val = None
        if self.has_error:
            self.error_val = letter_im

    def __repr__(self):
        return "<Item {}/{} sheet_no:{}, item_no: {}, val: {} pred: {} score: {}>".format(self.quiz_ref.username, self.quiz_ref.quiz_name, self.sheet_no, self.item_no, self.val, self.predicted_val, self.score)

    def __str__(self):
        return "Item: {}/{} {}-{} ({}) pred: {} score: {}".format(self.quiz_ref.username, self.quiz_ref.quiz_name, self.sheet_no, self.item_no, self.val, self.predicted_val, self.score)

    def letter_data(self):
        return np.ravel(self.letter_im).tolist()

    def letter_data_entry(self):
        username, quiz_name = (self.quiz_ref.username, \
                               self.quiz_ref.quiz_name)
        data_entry = [username, quiz_name, \
                      self.sheet_no, self.item_no, \
                      self.val] \
                     + self.letter_data()
        return data_entry



def non_errors_for_quiz(q):
    username, quiz_name = (q.username, q.quiz_name)
    sheet_count = io.count_sheets(username, quiz_name)
    cv_data = io.get_CV_data(username, quiz_name)
    sheets_with_errors = cv_data["sheets_with_errors"]
    # get items such that, 
    # * the sheet has no errors,
    # * it is not the reference sheet
    # * the item is correct.
    sheets_without_errors = [sheet_no for sheet_no in range(1, sheet_count) 
                             if (not (sheet_no in sheets_with_errors))]
    item_count = io.get_item_count(username, quiz_name)
    items = []
    answer_key = io.get_answer_key(username, quiz_name)
    corrections = io.get_corrections(username, quiz_name)
    for sheet_no in sheets_without_errors:
        items = items + [Item(q, sheet_no, item_no, correct_value_for_item(answer_key, item_no)) for item_no in range(item_count)
                        if item_is_correct(corrections, sheet_no, item_no)]
    return items


def letter_has_error(letter_im):
    return (isinstance(letter_im, dict) \
                        and "ERROR" in letter_im)
    

class Items:
    def __init__(self, quiz_ref, for_prediction=False):
        self.q = quiz_ref
        self.items = []
        self.for_prediction= for_prediction
        if(not for_prediction):
            self.corrections = self.q.get_corrections()
            self.answer_key = self.q.get_answer_key()

    def item_is_correct(self,sheet_no, item_no):
        return int(self.corrections[sheet_no][item_no]) >= 1


    def load_letters_2d(self, letters_in_quiz):
        items = []
        for sheet_no, letters_in_sheet in enumerate(letters_in_quiz):
            for item_no, letter_im in enumerate(letters_in_sheet):
                if self.for_prediction:
                    val = "???"
                    item = ItemImageData(self.q, \
                            sheet_no, \
                            item_no, \
                            val, \
                            letter_im)
                    items.append(item)
                elif self.item_is_correct(sheet_no, item_no) \
                        and not letter_has_error(letter_im):
                    val = self.answer_key[item_no]
                    item = ItemImageData(self.q, \
                            sheet_no, \
                            item_no, \
                            val, \
                            letter_im)
                    items.append(item)
        self.items = items
        return self.items

    def output_to_csv_rows(self):
        rows = [item.letter_data_entry() for item in self.items]
        return rows

    def write_to_csv(self):
        rows = [self.csv_headers()] + self.output_to_csv_rows()
        self.q.write_item_image_data_rows(rows)

    def csv_headers(self):
        letter_len = len(self.items[-1].letter_data())
        return ["username", "quiz_name", \
                      "sheet_no", "item_no", \
                      "val"] \
                     + ["Pixel{}".format(i) for i in range(letter_len)]


