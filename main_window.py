# import system module
import os
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, pyqtSignal
from yolov3.utils import detect_image_gui, detect_realtime, detect_video, Load_Yolo_model, detect_video_realtime_mp, \
    image_preprocess, postprocess_boxes, nms, draw_bbox
import tensorflow as tf
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import cv2

from ui_main_window import *

class realtime_detection(QtCore.QThread):
    def __init__(self):
        super(realtime_detection,self).__init__()
        self.yolo = Load_Yolo_model()
        self.input_size=416
        self.score_threshold=0.3
        self.iou_threshold=0.45
        self.CLASSES=80
        self.YOLO_INPUT_SIZE=320

    def run(self):
        detect_realtime(self.yolo, '', input_size=self.YOLO_INPUT_SIZE, show=True, rectangle_colors=(255, 0, 0))
        print("running successfully")

    def stop(self):
        self.terminate()

class image_detection(QtCore.QThread):
    sig=pyqtSignal(list)
    def __init__(self,img_path:str):
        super(image_detection,self).__init__()
        self.yolo = Load_Yolo_model()
        self.img_path=img_path

    def run(self):
        output_path = "D:/CUST/yolo/TensorFlow-2.x-YOLOv3/detection/detection.jpg"
        label=detect_image_gui(self.yolo, self.img_path, output_path, input_size=320, show=False,
                   rectangle_colors=(255, 0, 0))

        self.sig.emit(label)

    def stop(self):
        self.terminate()


class MainWindow(QWidget):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        super(MainWindow,self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.__file_name = ""
        # create a timer
        self.yolo = Load_Yolo_model()
        #realtime_paramerter
        self.input_size=416
        self.score_threshold=0.3
        self.iou_threshold=0.45
        self.CLASSES=80
        self.YOLO_INPUT_SIZE=320
        #real_time thread
        self.thread_realtime = realtime_detection()
        self._translate = QtCore.QCoreApplication.translate

        # set timer timeout callback function
        # # set control_bt callback clicked  function
        # self.ui.control_bt.clicked.connect(self.controlTimer)
        # self.ui.pushButton.clicked.connect(self.hand_detect)
        # self.ui.recognize.clicked.connect(self.recognize)
        self.ui.control_bt_2.clicked.connect(self.image_input)
        self.ui.detection.clicked.connect(self.image_detection)
        self.ui.pushButton.clicked.connect(self.realtime)
        self.status = True


    def image_input(self):
        self.__file_name, filetype = QFileDialog.getOpenFileName(self, "Open File", os.getcwd(),
                                                                 "Image Files (*.jpg);;All Files (*)")
        if self.__file_name:
            self.ui.label_import.setText(self.__file_name)
            self.file = open(self.__file_name, encoding='utf-8')
            self.ui.image_label.setPixmap(QtGui.QPixmap(self.__file_name))
            for i in range(14):
              self.ui.treeWidget.topLevelItem(i).setText(0, self._translate("Form", " "))
              self.ui.treeWidget.topLevelItem(i).setText(1, self._translate("Form", " "))

        else:
            pass

    def image_detection(self):
        if self.__file_name:
          self.img_pth = self.__file_name
          self.thread = image_detection(self.img_pth)
          self.thread.sig.connect(self.imgshow_thread)
          self.thread.start()
          # time.sleep(2)
          # output_path = "D:/CUST/yolo/TensorFlow-2.x-YOLOv3/IMAGES/detection.jpg"
          # self.ui.image_label.setPixmap(QtGui.QPixmap(output_path))
          # self.image_show()
        else:
            pass

    def imgshow_thread(self,list):
        self.label=list
        self.image_show()

    def image_show(self):
        output_path = "D:/CUST/yolo/TensorFlow-2.x-YOLOv3/detection/detection.jpg"
        self.ui.image_label.setPixmap(QtGui.QPixmap(output_path))
        for i in range (len(self.label)):
            object = ''.join(list(filter(str.isalpha, self.label[i])))
            confidence = ''.join(list(filter(lambda ch: ch in '0123456789.', self.label[i])))
            self.ui.treeWidget.topLevelItem(i).setText(0, self._translate("Form", object))
            self.ui.treeWidget.topLevelItem(i).setText(1, self._translate("Form", confidence))


    def realtime(self):
        if self.status == True:
            self.ui.pushButton.setText("Stop")
            self.status = False
            # detect_realtime(self.yolo, '', input_size=self.YOLO_INPUT_SIZE, show=True, rectangle_colors=(255, 0, 0))
            self.thread_realtime.start()
        else:
            self.thread_realtime.terminate()
            self.status = True
            self.ui.pushButton.setText("realtime detection")

    # view camera
    # def viewCam(self):
    #     pass
    #     # if self.detect_hand==False :
    #     #     # read image in BGR format
    #     #     ret, image = self.cap.read()
    #     #     # convert image to RGB format
    #     #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #     #     # get image infos
    #     #
    #     #     height, width, channel = image.shape
    #     #     step = channel * width
    #     #     # create QImage from image
    #     #     qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
    #     #     # show image in img_label
    #     #     self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))
    #     # elif self.detect_hand==True:
    #     #     ret, image = self.cap.read()
    #     #     # convert image to RGB format
    #     #     hands, image = self.detector.findHands(image)
    #     #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #     #     # get image infos
    #     #     height, width, channel = image.shape
    #     #     step = channel * width
    #     #     # create QImage from image
    #     #     qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
    #     #     # show image in img_label
    #     #     self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))
    #     #     if hands:
    #     #         hands1=hands[0]
    #     #         lmlist1=hands1["lmList"]
    #     #         bbox=hands1["bbox"]
    #     #         centerpoint=hands1["center"]
    #     #         handtype=hands1["type"]
    #     #         if self.recognize_state:
    #     #             lmlist1 = self.viewCam()
    #     #             lmlist1_array = np.array(lmlist1)
    #     #             print(lmlist1_array.shape)
    #     #         else:
    #     #             pass
    #
    # # start/stop timer
    # def controlTimer(self):
    #     pass
    #     # # if timer is stopped
    #     # if not self.timer.isActive():
    #     #     # create video capture
    #     #     self.cap = cv2.VideoCapture(0)
    #     #     # start timer
    #     #     self.timer.start(100)
    #     #     # update control_bt text
    #     #     self.ui.control_bt.setText("Stop")
    #     # # if timer is started
    #     # else:
    #     #     # stop timer
    #     #     self.timer.stop()
    #     #     # release video capture
    #     #     self.cap.release()
    #     #     # update control_bt text
    #     #     self.ui.control_bt.setText("Start")
    #
    # def hand_detect(self):
    #     pass
    #     # self.detect_hand=True
    #
    # def recognize(self):
    #     # self.recognize_state=True
    #     # if self.recognize_state:
    #     #     lmlist1 = self.viewCam()
    #     #     lmlist1_array = np.array(lmlist1)
    #     #     print(lmlist1_array.shape)
    #     # else:
    #     pass



