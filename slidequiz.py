from os import path
import json
from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal

class SlideQuiz(QObject):

    sig_slide_info = pyqtSignal(dict)
    sig_slide_quiz = pyqtSignal(dict)
    sig_slide_finish = pyqtSignal()
    sig_wrong_answer = pyqtSignal(int, int)
    sig_correct_answer = pyqtSignal(int, int)

    def __init__(self):
        self.path = None
        self.scores = [0,0,0,0]
        self.penalties = [0,0,0,0]
        self.slides = []
        self.current = 0
        super(SlideQuiz, self).__init__()

    def load(self, slides_path):
        self.path = slides_path
        with open(path.join(slides_path, 'slides.json'), 'r') as f:
            data = json.load(f)
            self.slides = data['slides']
        self.scores = [0,0,0,0]
        self.penalties = [0,0,0,0]
        self.current = -1
        for i,slide in enumerate(self.slides):
            self.slides[i]['status'] = 0
            self.slides[i]['src'] = path.join(self.path, self.slides[i]['src']) 
        self.next()

    def answer(self, player, answer):
        slide = self.slides[self.current]
        if slide['type'] == 'quiz' and slide['status'] != 2:
            if not self.penalties[player]:
                if slide['answer'] == answer:
                    self.slides[self.current]['status'] = 2 
                    self.scores[player] += slide['score']
                    self.sig_correct_answer.emit(player, self.scores[player])
                else:
                    self.penalties[player] += 2
                    self.sig_wrong_answer.emit(player, self.scores[player])

    def next(self):
        slide = None
        while 1:
            self.current += 1
            if self.current >= len(self.slides):
                slide = None
                break
            slide = self.slides[self.current]
            if (slide['type'] != 'quiz' or slide['status'] == 0):
                break
        if slide:
            if slide['type'] == 'info':
                self.sig_slide_info.emit(slide)
            elif slide['type'] == 'quiz':
                self.sig_slide_quiz.emit(slide)
                self.slides[self.current]['status'] = 1
                for i,score in enumerate(self.scores):
                    if self.penalties[i]:
                        self.penalties[i] -= 1
        else:
            self.sig_slide_finish.emit()

    def prev(self):
        slide = None
        while 1:
            if self.current == 0:
                slide = self.slides[0]
                break
            self.current -= 1
            slide = self.slides[self.current]
            if (slide['type'] == 'info'):
                break
        self.sig_slide_info.emit(slide)
