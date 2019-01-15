from sklearn import svm
import numpy as np
from joblib import dump, load
from quizitemfinder.steps.datacollector import ImageDataCollector
ML_SAVED_MODELS_FILE = './score_data/rmcc/clf_model.joblib'

class LetterPredictor:
    def __init__(self, quiz_ref, has_answers=True):
        self.quiz_ref = quiz_ref
        self.idc = ImageDataCollector(for_prediction=True)
        self.clf = load(ML_SAVED_MODELS_FILE) 
        self.value_whitelist = ['A', 'B', 'C', 'D']
        if has_answers:
            self.answer_key = self.quiz_ref.get_answer_key()
        else:
            self.answer_key = None

    def clean_items(self):
        items = self.idc.process_a_quiz(quiz_ref=self.quiz_ref)
        clean_items = [item for item in items.items if not item.has_error]
        item_count = self.quiz_ref.get_item_count()
        items_no_whitelist = [i for i in range(item_count) \
                              if \
                              self.answer_key[i] in self.value_whitelist]
        clean_items = [item for item in clean_items \
                       if \
                       item.item_no in items_no_whitelist]
        return clean_items
    
    def predict_item_val(self, item):
        letter_data = item.letter_data()
        predicted_val = self.clf.predict([letter_data])
        return predicted_val[0]
        
    def predict_items(self, clean_items):
        data_for_letters = [item.letter_data() for item in clean_items]
        predictions_for_letters = self.clf.predict(data_for_letters)
        for item, prediction in zip(clean_items, predictions_for_letters):
            # set letter prediction on item object
            item.predicted_val=prediction
            # score based on answer_key
            if self.answer_key is not None:
                if item.predicted_val == self.answer_key[item.item_no]:
                    item.score = 1
                else:
                    item.score = 0
                print(item)
        return clean_items
        
    def predict(self):
        items = self.clean_items()
        self.predicted_items = self.predict_items(items)
        return self.predicted_items

    def corrections2d(self, corrections=None):
        if corrections is None:
            corrections_dims = (self.quiz_ref.sheet_count,\
                                self.quiz_ref.get_item_count())
            corrections = np.full(corrections_dims, '???').tolist()
        
        answer_key = self.answer_key
            
        def score_item(item):
            print(item.predicted_val, answer_key[item.item_no], item.predicted_val == answer_key[item.item_no])
            if(item.predicted_val == answer_key[item.item_no]):
                return 1
            else: 
                return 0

        for i in self.predicted_items:
            score = score_item(i)
            corrections[i.sheet_no][i.item_no] = score_item(i)

        return corrections
    
    def predict_answer_key(self):
        ans_sheet = self.idc.process_a_sheet(self.quiz_ref, 1)
        letter_data = [item.letter_data() for item in ans_sheet]
        predictions = self.clf.predict(letter_data)
        return predictions
        #self.value_whitelist = ['A', 'B', 'C', 'D']

#quiz_ref = utils.QuizRef('rmcc', '107-2--4BH106--QUIZ-1')
#predictor = LetterPredictor(quiz_ref=quiz_ref, has_answers=True)
#answer_key = predictor.predict_answer_key()

#quiz_ref = utils.QuizRef('rmcc', '107-2--4BH106--QUIZ-1')
#predictor = LetterPredictor(quiz_ref=quiz_ref)
#ci = predictor.clean_items()
#print(ci[0])
#predictor.predict_item_val(ci[0])
#items = predictor.predict()
#print(items[0])
#predictor.corrections2d()
