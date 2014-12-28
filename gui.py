import time
import json
from os import path
from PyQt4 import QtCore
from PyQt4 import QtGui
from wiimote import WiimoteController
from slidequiz import SlideQuiz

# TODO: Provide a form element in the GUI
#       to let the user enter MAC addresses.
WIIMOTE_MAC_ADDRESSES = ('MAC-ADDRESS-1',
                         'MAC-ADDRESS-2',
                         'MAC-ADDRESS-3',
                         'MAC-ADDRESS-4',)

class MainWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.btn_start = QtGui.QPushButton('Configure wiimotes...')
        self.btn_next = QtGui.QPushButton('Next')
        self.btn_next.setEnabled(False)
        self.btn_prev = QtGui.QPushButton('Previous')
        self.btn_prev.setEnabled(False)
        self.btn_toggle = QtGui.QPushButton('Toggle screen mode')

        self.btn_toggle.clicked.connect(self.toggle_screen_mode)

        addresses = WIIMOTE_MAC_ADDRESSES
        self.wiimote = WiimoteController(addresses)
        self.wiimote_thread = QtCore.QThread()
        self.wiimote.moveToThread(self.wiimote_thread)
        self.wiimote.sig_button_pressed.connect(self.handle_button)
        self.wiimote.sig_ready.connect(self.handle_wiimotes_ready)
        self.btn_start.clicked.connect(self.wiimote.start)
        self.wiimote_thread.start()

        self.slidequiz = SlideQuiz()
        self.slidequiz_thread = QtCore.QThread()
        self.slidequiz.moveToThread(self.slidequiz_thread)
        self.slidequiz.sig_slide_quiz.connect(self.show_slide_quiz)
        self.slidequiz.sig_slide_info.connect(self.show_slide_info)
        self.slidequiz.sig_slide_finish.connect(self.show_slide_finish)
        self.slidequiz.sig_correct_answer.connect(self.handle_correct_answer)
        self.slidequiz.sig_wrong_answer.connect(self.handle_wrong_answer)
        self.btn_next.clicked.connect(self.slidequiz.next)
        self.btn_prev.clicked.connect(self.slidequiz.prev)
        self.slidequiz_thread.start()

        layout = QtGui.QGridLayout(self)

        self.imageLabel = QtGui.QLabel()
        layout.addWidget(self.imageLabel, 0, 0, 1, 4)

        self.players = []
        for i in range(4):
            self.players.append(QtGui.QLabel())
            self.players[i].setText('<h1>P{}: 0</h1>'.format(i+1))
            layout.addWidget(self.players[i], 1, 1+i, 1, 1)
        layout.addWidget(self.btn_start, 2, 2)
        layout.addWidget(self.btn_next, 2, 0)
        layout.addWidget(self.btn_prev, 2, 1)
        layout.addWidget(self.btn_toggle, 2, 3)
        layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.setLayout(layout)
        self.imageLabel.setPixmap(QtGui.QPixmap('./assets/wiimote.gif'))

    def toggle_screen_mode(self):
        if self.windowState() & QtCore.Qt.WindowFullScreen:
            self.showNormal()
        else:
            self.showFullScreen()

    def show_slide_quiz(self, slide):
        self.show_image(slide['src'])
        for player in range(4):
            if self.slidequiz.penalties[player]:
                self.players[player].setStyleSheet('color: yellow;')
            else:
                self.players[player].setStyleSheet('color: black;')

    def show_slide_info(self, slide):
        self.show_image(slide['src'])
        for player in range(4):
            self.players[player].setStyleSheet('color: black;')

    def show_slide_finish(self):
        print('Finish!')

    def show_image(self, path):
        self.imageLabel.setPixmap(QtGui.QPixmap(path))

    def handle_wiimotes_ready(self):
        ruta = QtGui.QFileDialog.getExistingDirectory(self, 
            'Presentation directory',
            '/home')
        self.btn_start.setEnabled(False)
        self.btn_next.setEnabled(True)
        self.btn_prev.setEnabled(True)
        self.slidequiz.load(str(ruta))
        self.showFullScreen()

    def handle_button(self, player, button):
        print('Wiimote #{} pressed {} button.'.format(player, button))
        self.slidequiz.answer(player, button)

    def handle_wrong_answer(self, player, score):
        self.players[player].setStyleSheet('color: red;')
        self.players[player].setText('<h1>P{} : {}</h1>'.format(player+1, score))
        print('Wrong answer by {}. Score: {}'.format(player, score))

    def handle_correct_answer(self, player, score):
        self.players[player].setStyleSheet('color: green;')
        self.players[player].setText('<h1>P{} : {}</h1>'.format(player+1, score))
        print('Correct answer by {}. Score: {}'.format(player, score))
