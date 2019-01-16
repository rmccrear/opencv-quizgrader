from quizitemfinder.io import open_rects as cached_cells
import quizitemfinder.steps.utils as utils
from quizitemfinder.steps.step1errorfix import fix_sheet_errors

from collections import namedtuple
Rect = namedtuple('Rect', ['x', 'y', 'w', 'h'])
def rectdims(pts):
    upperleft, lowerright = pts
    x, y = upperleft
    x1, y1 = lowerright
    w = x1-x
    h = y1-y
    return Rect(x=x, y=y, w=w, h=h)

Ave = namedtuple('Ave', ['mean', 'max', 'min'])

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

class CellFinder:

    def __init__(self, username=None, quiz_name=None, quiz_ref=None):
        if username is not None and quiz_name is not None:
            self.username, self.quiz_name = (username, quiz_name)
            self.quiz_ref = utils.QuizRef(username, quiz_name)
        else:
            self.username, self.quiz_name = (quiz_ref.username, quiz_ref.quiz_name)
            self.quiz_ref = quiz_ref

        self.cells = None

    def find_cells(self):
        raw_cells = self.__process_cells()
        fixed_cells = fix_sheet_errors(raw_cells, self.quiz_ref)
        return fixed_cells

    def find_reference_cells(self):
        return self.__process_cells()[0]

    def average_item_width(self):
        items = self.cells[0]['items']
        widths = [rectdims(c).w for c in items ]
        return Ave(mean=mean(widths), max=max(widths), min=min(widths))

    def average_item_height(self):
        items = self.cells[0]['items']
        heights = [rectdims(c).h for c in items]
        return Ave(mean=mean(heights), max=max(heights), min=min(heights))

    def __process_cells(self):
        username, quiz_name = (self.username, self.quiz_name)
        if self.cells is None:
            self.cells = cached_cells(username, quiz_name)
        return self.cells

    
    # todo: put find rects fns here
    # def __find_rects(im):


class Demo:
    def __init__(self, username=None, quiz_name=None, quiz_ref=None):
        if username is not None and quiz_name is not None:
            self.username, self.quiz_name = (username, quiz_name)
            self.cf = CellFinder(username, quiz_name)
        else:
            self.username, self.quiz_name = (quiz_ref.username, quiz_ref.quiz_name)
            self.cf = CellFinder(quiz_ref=quiz_ref)

    def show(self):
        import quizitemfinder.io as io
        im1 = io.open_sheet_im(self.username, self.quiz_name, 0)
        cf_bh = CellFinder(self.username, self.quiz_name)
        refcells=cf_bh.find_reference_cells()
        utils.showim(im1, title="original")
        firstitem_rect = refcells["items"][0]
        boxxed_im = utils.drawrect(im1, firstitem_rect)
        utils.showim(boxxed_im, title="find item[0]")
        firstitem_im=utils.croprect(im1, firstitem_rect)
        utils.showim(firstitem_im, title="crop item[0]")

import unittest
class TestCellFinder(unittest.TestCase):
        def test_cellfinder_cellcount(self):
            cf = CellFinder('rmcc', '107-2--4BH106--QUIZ-1')
            headers, items = (cf.find_reference_cells()["headers"], cf.find_reference_cells()["items"])
            self.assertTrue(len(headers) == 3)
            self.assertTrue(len(items) == 20)

if __name__ == '__main__':
    unittest.main()
