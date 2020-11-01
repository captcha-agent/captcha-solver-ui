# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from requests import post
import urllib.request
from configparser import ConfigParser


class CaptchaSolver(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.conf = ConfigParser()
        self.conf.sections()
        self.conf.read('conf.ini')
        self.__check_api_key__()

        self.centralwidget = QtWidgets.QWidget(self)
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.next = QtWidgets.QPushButton(self.centralwidget)
        self.picture_1 = QtWidgets.QLabel(self.centralwidget)
        self.picture_2 = QtWidgets.QLabel(self.centralwidget)
        self.picture_3 = QtWidgets.QLabel(self.centralwidget)
        self.picture_4 = QtWidgets.QLabel(self.centralwidget)
        self.picture_5 = QtWidgets.QLabel(self.centralwidget)
        self.picture_6 = QtWidgets.QLabel(self.centralwidget)
        self.picture_7 = QtWidgets.QLabel(self.centralwidget)
        self.picture_8 = QtWidgets.QLabel(self.centralwidget)
        self.picture_9 = QtWidgets.QLabel(self.centralwidget)
        self.pictures = [self.picture_1, self.picture_2, self.picture_3,
                         self.picture_4, self.picture_5, self.picture_6,
                         self.picture_7, self.picture_8, self.picture_9]

        self.clicked_pictures = [False] * 9
        self.current_captcha_data = ()
        self.setup_ui()
        self.show()

    def setup_ui(self):
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle('reCAPTCHA')
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.resize(330, 480)
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
        self.picture_1.mousePressEvent = self.click_pic_1
        self.picture_2.mousePressEvent = self.click_pic_2
        self.picture_3.mousePressEvent = self.click_pic_3
        self.picture_4.mousePressEvent = self.click_pic_4
        self.picture_5.mousePressEvent = self.click_pic_5
        self.picture_6.mousePressEvent = self.click_pic_6
        self.picture_7.mousePressEvent = self.click_pic_7
        self.picture_8.mousePressEvent = self.click_pic_8
        self.picture_9.mousePressEvent = self.click_pic_9

        self.title.setStyleSheet('font: 30pt Calibri')
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setText('Titel')

        self.next.setText('Next')
        self.next.setShortcut('Space')

        self.__refresh_captcha__()

    # ------------------------ Click methods ------------------------
    def click_pic_1(self, event):
        self.__handle_picture_click__(0)

    def click_pic_2(self, event):
        self.__handle_picture_click__(1)

    def click_pic_3(self, event):
        self.__handle_picture_click__(2)

    def click_pic_4(self, event):
        self.__handle_picture_click__(3)

    def click_pic_5(self, event):
        self.__handle_picture_click__(4)

    def click_pic_6(self, event):
        self.__handle_picture_click__(5)

    def click_pic_7(self, event):
        self.__handle_picture_click__(6)

    def click_pic_8(self, event):
        self.__handle_picture_click__(7)

    def click_pic_9(self, event):
        self.__handle_picture_click__(8)

    def click_next(self):
        if sum(self.clicked_pictures) == 3:
            self.__submit_captcha__()
            self.__refresh_captcha__()

    # ----------------------- Private methods -----------------------
    def __handle_picture_click__(self, pic_id):
        if not self.clicked_pictures[pic_id]:
            self.pictures[pic_id].setStyleSheet("border: 3px solid red;")
        else:
            self.pictures[pic_id].setStyleSheet("")
        self.clicked_pictures[pic_id] = not self.clicked_pictures[pic_id]

    def __submit_captcha__(self):
        res = post(self.conf['srv']['path'] + '/picture/submit', json={'id': self.current_captcha_data['id'], 'correct_pics': self.clicked_pictures})
        if res.status_code != 200:
            self.__error_msg__('Server error', 'Internal server error. Pleas check server log.')

        self.clicked_pictures = [False] * 9
        for i in self.pictures:
            i.setStyleSheet("")

    def __refresh_captcha__(self):
        res = post(self.conf['srv']['path'] + '/picture/get', json={'typ': self.conf.getint('user', 'typ')})
        if res.status_code != 200:
            self.__error_msg__('Server error', 'Internal server error. Pleas check server log.')
        if res.json()['data']['id'] == -1:
            self.__error_msg__('No more Pictures', 'All pictures are solved. Pleas generate new ones.')

        self.current_captcha_data = res.json()['data']
        self.title.setText(self.current_captcha_data['titel'])
        for i, j in zip(self.current_captcha_data['pics'], self.pictures):
            print(i)
            data = urllib.request.urlopen(i).read()
            image = QtGui.QImage()
            image.loadFromData(data)
            j.setPixmap(QtGui.QPixmap(image))

    def __error_msg__(self, title, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(title)
        msg.setInformativeText(text)
        msg.setWindowTitle("Error")
        msg.exec_()
        quit()

    def __check_api_key__(self):
        res = post(self.conf['srv']['path'] + '/api-key', json={'key': self.conf['srv']['key']})
        if not res.json()['verified']:
            self.__error_msg__('Wrong API key', 'Your API key got rejected. Pleas provide a verified key.')


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = CaptchaSolver()
    sys.exit(app.exec_())
