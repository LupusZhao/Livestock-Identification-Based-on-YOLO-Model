# -*- coding: utf-8 -*-
import os
import sys
import cv2
import numpy as np
import time
import warnings
import torch
import threading
from pathlib import Path
from PySide6.QtGui import *
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from ultralytics import YOLO
from ui import Ui_MainWindow


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

warnings.filterwarnings('ignore')
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, model_path):
        super().__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.stop = False
        self.file_path = ""
        # 图片读取进程
        self.output_size = 640
        self.img2predict = ""
        # 更新视频图像
        self.timer_camera = QTimer()
        self.cap = None
        self.is_camera_open = False
        self.stopEvent = threading.Event()
        # 加载检测模型
        self.model = YOLO(model_path, task='detect')
        self.model(np.zeros((48, 48, 3)))  # 预先加载推理模型

        self.setupUi(self)
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.pushButton.clicked.connect(self.upload_img)
        self.pushButton_2.clicked.connect(self.open_mp4)
        self.pushButton_3.clicked.connect(self.open_cam)
        self.pushButton_4.clicked.connect(self.stop_vid)
        self.comboBox.activated.connect(self.combox_change)

    def _sync_canvas_overlay(self, image_shape, location_list, cls_list, names, conf_raw, infer_time):
        if not hasattr(self.label_3, 'set_overlay_boxes'):
            return
        h, w = image_shape[:2]
        if h <= 0 or w <= 0:
            return

        boxes = []
        for i, xyxy in enumerate(location_list):
            x1, y1, x2, y2 = xyxy
            boxes.append((
                x1 / w,
                y1 / h,
                x2 / w,
                y2 / h,
                names[cls_list[i]],
                conf_raw[i],
            ))
        self.label_3.set_overlay_boxes(boxes)
        fps = "{:.1f}".format(1.0 / max(infer_time, 1e-6))
        self.label_3.set_hud_info(fps=fps, model='YOLO', objects=len(boxes))

    def upload_img(self):
        """上传图片"""
        # 选择录像文件进行读取
        self.comboBox.setDisabled(False)
        self.pushButton_4.setEnabled(False)
        fileName, fileType = QFileDialog.getOpenFileName(self, 'Choose file', '', '*.jpg *.png *.tif *.jpeg')
        if fileName:
            self.file_path = fileName
            """检测图片"""
            org_path = self.file_path
            # 目标检测
            t1 = time.time()
            results = self.model.predict(org_path, conf=0.25)[0]
            names = results.names
            t2 = time.time()
            self.label_6.setText('{:.3f} s'.format(t2 - t1))
            now_img = results.plot()
            self.resize_scale = self.output_size / now_img.shape[0]
            im0 = cv2.resize(now_img, (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            cv2.imwrite("middle_file/tmp/single_result.jpg", im0)
            self.label_3.setScaledContents(True)
            self.label_3.setPixmap(QPixmap("middle_file//tmp/single_result.jpg"))

            location_list = results.boxes.xyxy.tolist()
            location_list = [list(map(int, e)) for e in location_list]
            cls_list = results.boxes.cls.tolist()
            cls_list = [int(i) for i in cls_list]
            conf_raw = results.boxes.conf.tolist()
            conf_list = conf_raw.copy()
            conf_list = ['%.2f %%' % (each * 100) for each in conf_list]

            total_nums = len(location_list)
            self.label_11.setText(str(total_nums))

            choose_list = ['全部']
            target_names = [names[id] + '_' + str(index) for index, id in enumerate(cls_list)]
            choose_list = choose_list + target_names
            self.comboBox.clear()
            self.comboBox.addItems(choose_list)

            self.results = results
            self.names = names
            self.cls_list = cls_list
            self.conf_list = conf_list
            self.location_list = location_list
            self.conf_raw = conf_raw
            self.current_frame_shape = now_img.shape
            self._sync_canvas_overlay(now_img.shape, location_list, cls_list, names, conf_raw, t2 - t1)

            if total_nums >= 1:
                self.label_16.setText(names[cls_list[0]])
                self.label_15.setText(str(conf_list[0]))
                #   默认显示第一个目标框坐标
                #   设置坐标位置值
                self.label_13.setText(str(location_list[0][0]))
                self.label_19.setText(str(location_list[0][1]))
                self.label_21.setText(str(location_list[0][2]))
                self.label_23.setText(str(location_list[0][3]))
            else:
                self.label_16.setText(' ')
                self.label_15.setText(' ')
                self.label_13.setText(' ')
                self.label_19.setText(' ')
                self.label_21.setText(' ')
                self.label_23.setText(' ')

    def combox_change(self):
        com_text = self.comboBox.currentText()
        if com_text == '全部':
            cur_box = self.location_list
            cur_img = self.results.plot()
            self.label_16.setText(self.names[self.cls_list[0]])
            self.label_15.setText(str(self.conf_list[0]))
        else:
            index = int(com_text.split('_')[-1])
            cur_box = [self.location_list[index]]
            cur_img = self.results[index].plot()
            self.label_16.setText(self.names[self.cls_list[index]])
            self.label_15.setText(str(self.conf_list[index]))

        if hasattr(self, 'conf_raw') and hasattr(self, 'current_frame_shape') and hasattr(self.label_3, 'set_overlay_boxes'):
            if com_text == '全部':
                self._sync_canvas_overlay(
                    self.current_frame_shape,
                    self.location_list,
                    self.cls_list,
                    self.names,
                    self.conf_raw,
                    0.03,
                )
            else:
                self._sync_canvas_overlay(
                    self.current_frame_shape,
                    [self.location_list[index]],
                    [self.cls_list[index]],
                    self.names,
                    [self.conf_raw[index]],
                    0.03,
                )

        # 设置坐标位置值
        self.label_13.setText(str(cur_box[0][0]))
        self.label_19.setText(str(cur_box[0][1]))
        self.label_21.setText(str(cur_box[0][2]))
        self.label_23.setText(str(cur_box[0][3]))

        resize_cvimg = cv2.resize(cur_img, (0, 0), fx=self.resize_scale, fy=self.resize_scale)
        pix_img = self.cvimg_to_qpiximg(resize_cvimg)
        self.label_3.clear()
        self.label_3.setScaledContents(True)
        self.label_3.setPixmap(pix_img)
        self.label_3.setAlignment(Qt.AlignCenter)

    def cvimg_to_qpiximg(self, cvimg):
        height, width, depth = cvimg.shape
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
        qimg = QImage(cvimg.data, width, height, width * depth, QImage.Format_RGB888)
        qpix_img = QPixmap(qimg)
        return qpix_img

    def get_video_path(self):
        file_path, _ = QFileDialog.getOpenFileName(None, '打开视频', './', "Image files (*.avi *.mp4)")
        if not file_path:
            return None
        self.org_path = file_path
        return file_path

    def video_start(self):
        # 定时器开启，每隔一段时间，读取一帧
        self.timer_camera.start(1)
        self.timer_camera.timeout.connect(self.open_frame)

    def video_stop(self):
        self.cap.release()
        self.timer_camera.stop()

    def open_frame(self):
        ret, now_img = self.cap.read()
        if ret:
            input_shape = now_img.shape
            # 目标检测
            t1 = time.time()
            results = self.model.predict(now_img, conf=0.25)[0]
            names = results.names
            t2 = time.time()
            self.label_6.setText('{:.3f} s'.format(t2 - t1))
            now_img = results.plot()
            self.resize_scale = self.output_size / now_img.shape[0]
            im0 = cv2.resize(now_img, (0, 0), fx=self.resize_scale, fy=self.resize_scale)
            cv2.imwrite("middle_file//tmp/single_result_vid.jpg", im0)
            self.label_3.setScaledContents(True)
            self.label_3.setPixmap(QPixmap("middle_file//tmp/single_result_vid.jpg"))

            location_list = results.boxes.xyxy.tolist()
            location_list = [list(map(int, e)) for e in location_list]
            cls_list = results.boxes.cls.tolist()
            cls_list = [int(i) for i in cls_list]
            conf_raw = results.boxes.conf.tolist()
            conf_list = conf_raw.copy()
            conf_list = ['%.2f %%' % (each * 100) for each in conf_list]

            total_nums = len(location_list)
            self.label_11.setText(str(total_nums))

            choose_list = ['全部']
            target_names = [names[id] + '_' + str(index) for index, id in enumerate(cls_list)]
            choose_list = choose_list + target_names
            self.comboBox.clear()
            self.comboBox.addItems(choose_list)

            self.results = results
            self.names = names
            self.cls_list = cls_list
            self.conf_list = conf_list
            self.location_list = location_list
            self.conf_raw = conf_raw
            self.current_frame_shape = input_shape
            self._sync_canvas_overlay(input_shape, location_list, cls_list, names, conf_raw, t2 - t1)

            if total_nums >= 1:
                self.label_16.setText(names[cls_list[0]])
                self.label_15.setText(str(conf_list[0]))
                #   默认显示第一个目标框坐标
                #   设置坐标位置值
                self.label_13.setText(str(location_list[0][0]))
                self.label_19.setText(str(location_list[0][1]))
                self.label_21.setText(str(location_list[0][2]))
                self.label_23.setText(str(location_list[0][3]))
            else:
                self.label_16.setText(' ')
                self.label_15.setText(' ')
                self.label_13.setText(' ')
                self.label_19.setText(' ')
                self.label_21.setText(' ')
                self.label_23.setText(' ')
        else:
            self.cap.release()
            self.timer_camera.stop()

    def open_cam(self):
        """开启摄像头检测事件"""
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(True)
        self.comboBox.clear()
        self.comboBox.setDisabled(True)

        self.is_camera_open = not self.is_camera_open
        if self.is_camera_open:
            print('摄像头开启')
            self.cap = cv2.VideoCapture(0)
            self.video_start()
        else:
            print('摄像头未开启')
            self.label_3.setText('')
            if self.cap:
                self.cap.release()
                cv2.destroyAllWindows()
            self.label_3.clear()

    def open_mp4(self):
        """开启视频文件检测事件"""
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(True)
        self.comboBox.clear()
        self.comboBox.setDisabled(True)

        if self.is_camera_open:
            self.is_camera_open = False
            print('摄像头未开启')

        video_path = self.get_video_path()
        if not video_path:
            return None
        self.cap = cv2.VideoCapture(video_path)
        self.video_start()

    def stop_vid(self):
        """窗口关闭事件"""
        self.stopEvent.set()
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(False)
        if self.cap:
            self.cap.release()
        self.is_camera_open = False
        if hasattr(self.label_3, 'set_overlay_boxes'):
            self.label_3.set_overlay_boxes([])
            self.label_3.set_hud_info(objects=0)


if __name__ == '__main__':
    # todo 修改模型权重路径
    model_dir = "D:\浏览器下载\livestock\livestock\livestock_detection\\runs\detect\\train\weights\\best.pt"

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    my_window = MyWindow(model_dir)
    my_window.show()
    sys.exit(app.exec_())

