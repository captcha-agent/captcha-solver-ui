# -*- coding: utf-8 -*-
from requests import post
import urllib.request
from configparser import ConfigParser
from os import system
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QLabel,
    QPushButton,
    QWidget,
    QMessageBox,
    QAction,
    qApp,
)


class CaptchaSolver(QMainWindow):
    def __init__(self):
        super().__init__()
        self.centralwidget = QWidget(self)
        self.title = QLabel(self.centralwidget)
        self.next = QPushButton(self.centralwidget)
        self.picture_1 = QLabel(self.centralwidget)
        self.picture_2 = QLabel(self.centralwidget)
        self.picture_3 = QLabel(self.centralwidget)
        self.picture_4 = QLabel(self.centralwidget)
        self.picture_5 = QLabel(self.centralwidget)
        self.picture_6 = QLabel(self.centralwidget)
        self.picture_7 = QLabel(self.centralwidget)
        self.picture_8 = QLabel(self.centralwidget)
        self.picture_9 = QLabel(self.centralwidget)
        self.pictures = [self.picture_1, self.picture_2, self.picture_3,
                         self.picture_4, self.picture_5, self.picture_6,
                         self.picture_7, self.picture_8, self.picture_9]

        self.clicked_pictures = [False] * 9
        self.current_captcha_data = ()

        self.__load_conf__(True)
        self.setup_ui()
        self.show()

    def setup_ui(self):
        menu_file_get_new_image = QAction('&Get new Images', self)
        menu_file_get_new_image.setStatusTip('Downloads Captchas (Use with Hotspot)')
        menu_file_get_new_image.triggered.connect(lambda: system("start cmd /k GetData.exe"))
        menu_file_reload_config = QAction('&Reload config', self)
        menu_file_reload_config.setStatusTip('Reloads config file')
        menu_file_reload_config.triggered.connect(self.__load_conf__)
        menu_file_exit = QAction('&Exit', self)
        menu_file_exit.setStatusTip('Exit application')
        menu_file_exit.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        menu_file = menubar.addMenu('File')
        menu_file.addAction(menu_file_get_new_image)
        menu_file.addAction(menu_file_reload_config)
        menu_file.addAction(menu_file_exit)

        self.statusBar().show()
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle('reCAPTCHA')
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.resize(330, 500)
        self.title.setGeometry(QtCore.QRect(20, 10, 290, 60))
        self.next.setGeometry(QtCore.QRect(20, 400, 290, 60))
        self.picture_1.setGeometry(QtCore.QRect(20, 100, 90, 90))
        self.picture_2.setGeometry(QtCore.QRect(120, 100, 90, 90))
        self.picture_3.setGeometry(QtCore.QRect(220, 100, 90, 90))
        self.picture_4.setGeometry(QtCore.QRect(20, 200, 90, 90))
        self.picture_5.setGeometry(QtCore.QRect(120, 200, 90, 90))
        self.picture_6.setGeometry(QtCore.QRect(220, 200, 90, 90))
        self.picture_7.setGeometry(QtCore.QRect(20, 300, 90, 90))
        self.picture_8.setGeometry(QtCore.QRect(120, 300, 90, 90))
        self.picture_9.setGeometry(QtCore.QRect(220, 300, 90, 90))

        self.next.clicked.connect(self.click_next)
        self.picture_1.mousePressEvent = lambda event: self.__handle_picture_click__(0)
        self.picture_2.mousePressEvent = lambda event: self.__handle_picture_click__(1)
        self.picture_3.mousePressEvent = lambda event: self.__handle_picture_click__(2)
        self.picture_4.mousePressEvent = lambda event: self.__handle_picture_click__(3)
        self.picture_5.mousePressEvent = lambda event: self.__handle_picture_click__(4)
        self.picture_6.mousePressEvent = lambda event: self.__handle_picture_click__(5)
        self.picture_7.mousePressEvent = lambda event: self.__handle_picture_click__(6)
        self.picture_8.mousePressEvent = lambda event: self.__handle_picture_click__(7)
        self.picture_9.mousePressEvent = lambda event: self.__handle_picture_click__(8)

        self.title.setStyleSheet('font: 30pt Calibri')
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setText('Titel')

        self.next.setText('Next')
        self.next.setShortcut('Space')

        self.__load_captcha__()

    # ------------------------ Click methods ------------------------
    def click_next(self):
        if sum(self.clicked_pictures) == 3:
            self.__submit_captcha__()
            self.__load_captcha__()

    # ----------------------- Private methods -----------------------
    def __handle_picture_click__(self, pic_id):
        if not self.clicked_pictures[pic_id]:
            self.pictures[pic_id].setStyleSheet("border: 3px solid red;")
        else:
            self.pictures[pic_id].setStyleSheet("")
        self.clicked_pictures[pic_id] = not self.clicked_pictures[pic_id]

    def __submit_captcha__(self):
        res = post(self.conf['server']['path'] + '/picture/submit', json={'id': self.current_captcha_data['id'], 'correct_pics': self.clicked_pictures})
        if res.status_code != 200:
            self.__error_msg__('Server error', 'Internal server error. Pleas check server log.')
        self.__reset_view__()

    def __reset_view__(self):
        self.clicked_pictures = [False] * 9
        for i in self.pictures:
            i.setStyleSheet("")

    def __load_captcha__(self):
        res = post(self.conf['server']['path'] + '/picture/get', json={'typ': self.conf['solver']['typ']})
        if res.status_code != 200:
            self.__error_msg__('Server error', 'Internal server error. Pleas check server log.')
        if res.json()['data']['id'] == -1:
            self.__error_msg__('No more Pictures', 'All pictures are solved. Pleas generate new ones.')

        self.current_captcha_data = res.json()['data']
        self.title.setText(self.current_captcha_data['titel'])
        for i, j in zip(self.current_captcha_data['pics'], self.pictures):
            print(self.conf['server']['path'] + i)
            data = urllib.request.urlopen(self.conf['server']['path'] + i).read()
            image = QtGui.QImage()
            image.loadFromData(data)
            j.setPixmap(QtGui.QPixmap(image))

    def __error_msg__(self, title, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(title)
        msg.setInformativeText(text)
        msg.setWindowTitle("Error")
        msg.exec_()
        quit()

    def __check_api_key__(self):
        res = post(self.conf['server']['path'] + '/api-key', json={'key': self.conf['server']['key']})
        if not res.json()['verified']:
            self.__error_msg__('Wrong API key', 'Your API key got rejected. Pleas provide a verified key.')



    def __load_conf__(self, first=False):
        self.conf = ConfigParser()
        self.conf.sections()
        self.conf.read('conf.ini')
        self.__check_api_key__()
        if not first:
            self.__reset_view__()
            self.__load_captcha__()



if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ui = CaptchaSolver()
    sys.exit(app.exec_())
