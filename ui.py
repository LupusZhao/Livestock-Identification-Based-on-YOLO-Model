# -*- coding: utf-8 -*-

from PySide6.QtCore import QCoreApplication, QMetaObject, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QToolBox,
    QVBoxLayout,
    QWidget,
)


PALETTE = {
    "green": "#2E7D32",
    "ivory": "#FAFAF5",
    "wood": "#D7CCC8",
    "text": "#1B3C1D",
    "muted": "#5F6F58",
    "danger": "#C62828",
}


class GreenButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(38)
        self.setStyleSheet(
            """
            QPushButton {
                background: #2E7D32;
                color: #FAFAF5;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover { background: #276A2A; }
            QPushButton:pressed { background: #1F5722; }
            QPushButton:disabled { background: #95AF96; }
            """
        )


class HoverCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hovering = False
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("hover_card")
        self.setStyleSheet(
            """
            QFrame#hover_card {
                background: #FFFFFF;
                border: 1px solid #E0E6DC;
                border-radius: 14px;
            }
            """
        )

    def enterEvent(self, event):
        self._hovering = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovering = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._hovering:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(QColor("#A5C7A7"), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 14, 14)


class StatCard(HoverCard):
    def __init__(self, title, value, tip="", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #5F6F58; font-size: 12px;")
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #1B3C1D; font-size: 22px; font-weight: 700;")
        tip_label = QLabel(tip)
        tip_label.setStyleSheet("color: #739574; font-size: 11px;")
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(tip_label)


class DonutWidget(QWidget):
    def __init__(self, percent=65, title="环境稳定度", parent=None):
        super().__init__(parent)
        self.percent = percent
        self.title = title
        self.setMinimumSize(180, 180)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(24, 24, -24, -24)
        painter.setPen(QPen(QColor("#DCE6D8"), 14))
        painter.drawArc(rect, 0, 360 * 16)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor("#2E7D32"))
        gradient.setColorAt(1.0, QColor("#6E9E71"))
        painter.setPen(QPen(gradient, 14))
        painter.drawArc(rect, 90 * 16, int(-self.percent / 100 * 360 * 16))

        painter.setPen(QColor("#1B3C1D"))
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self.percent}%")

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor("#5F6F58"))
        title_rect = self.rect().adjusted(0, int(self.height() * 0.60), 0, 0)
        painter.drawText(title_rect, Qt.AlignHCenter, self.title)


class MiniBarChart(QWidget):
    def __init__(self, values=None, labels=None, parent=None):
        super().__init__(parent)
        self.values = values or [28, 34, 31, 39, 42, 36, 45]
        self.labels = labels or ["一", "二", "三", "四", "五", "六", "日"]
        self.setMinimumHeight(160)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        area = self.rect().adjusted(20, 16, -14, -28)
        max_val = max(self.values) if self.values else 1
        count = len(self.values)
        if count == 0:
            return

        bar_gap = 12
        bar_w = max(12, (area.width() - bar_gap * (count - 1)) // count)
        for i, val in enumerate(self.values):
            ratio = val / max_val
            h = int(area.height() * ratio)
            x = area.left() + i * (bar_w + bar_gap)
            y = area.bottom() - h

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#D7CCC8"))
            painter.drawRoundedRect(QRectF(x, area.top(), bar_w, area.height()), 6, 6)

            painter.setBrush(QColor("#2E7D32"))
            painter.drawRoundedRect(QRectF(x, y, bar_w, h), 6, 6)

            painter.setPen(QColor("#5F6F58"))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(QRectF(x - 6, area.bottom() + 6, bar_w + 12, 18), Qt.AlignCenter, self.labels[i])


class ChickenAvatar(QWidget):
    def __init__(self, name="M1", parent=None):
        super().__init__(parent)
        self.name = name[:2].upper()
        self.setFixedSize(46, 46)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FFEBD8"))
        painter.drawEllipse(0, 0, 46, 46)

        painter.setBrush(QColor("#FBC16E"))
        painter.drawEllipse(11, 9, 24, 24)

        painter.setBrush(QColor("#F58A42"))
        beak = QPainterPath()
        beak.moveTo(23, 18)
        beak.lineTo(28, 21)
        beak.lineTo(23, 24)
        beak.closeSubpath()
        painter.drawPath(beak)

        painter.setPen(QColor("#5B391A"))
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.drawText(self.rect().adjusted(0, 26, 0, 0), Qt.AlignCenter, self.name)


class YoloIndicator(QWidget):
    def __init__(self, text="YOLO Ready", active=True, parent=None):
        super().__init__(parent)
        self.text = text
        self.active = active
        self.setMinimumHeight(28)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        dot_color = QColor("#2E7D32") if self.active else QColor("#C62828")
        painter.setPen(Qt.NoPen)
        painter.setBrush(dot_color)
        painter.drawEllipse(8, 8, 12, 12)
        painter.setPen(QColor("#1B3C1D"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Medium))
        painter.drawText(self.rect().adjusted(28, 0, 0, 0), Qt.AlignVCenter, self.text)


class YoloCanvas(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._boxes = []
        self._info = {
            "fps": "--",
            "model": "YOLO",
            "cam": "CAM-01",
            "objects": 0,
        }
        self.setMinimumSize(720, 420)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "background: #0D1A10; border: 1px solid #28432A; border-radius: 14px; color: #D6E7D7;"
        )
        self.setText("YOLO Canvas")

    def set_overlay_boxes(self, boxes):
        self._boxes = boxes
        self.update()

    def set_hud_info(self, fps=None, model=None, cam=None, objects=None):
        if fps is not None:
            self._info["fps"] = fps
        if model is not None:
            self._info["model"] = model
        if cam is not None:
            self._info["cam"] = cam
        if objects is not None:
            self._info["objects"] = objects
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        content_rect = self.contentsRect().adjusted(10, 10, -10, -10)
        if not self._boxes and self.pixmap() is None:
            demo_boxes = [
                (0.18, 0.22, 0.35, 0.50, "hen", 0.94),
                (0.58, 0.28, 0.80, 0.62, "egg", 0.88),
            ]
        else:
            demo_boxes = self._boxes

        pen = QPen(QColor("#9EF8A2"), 2)
        painter.setPen(pen)
        for b in demo_boxes:
            if len(b) < 6:
                continue
            x1, y1, x2, y2, cls_name, conf = b
            box = QRectF(
                content_rect.left() + x1 * content_rect.width(),
                content_rect.top() + y1 * content_rect.height(),
                max(2.0, (x2 - x1) * content_rect.width()),
                max(2.0, (y2 - y1) * content_rect.height()),
            )
            painter.drawRoundedRect(box, 3, 3)

            badge = QRectF(box.left(), max(6.0, box.top() - 24), 146, 20)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(46, 125, 50, 210))
            painter.drawRoundedRect(badge, 6, 6)
            painter.setPen(QColor("#FAFAF5"))
            painter.setFont(QFont("Consolas", 8, QFont.Bold))
            painter.drawText(badge.adjusted(8, 0, -6, 0), Qt.AlignVCenter, f"{cls_name}  {conf * 100:.1f}%")
            painter.setPen(pen)

        hud_rect = QRectF(content_rect.left(), content_rect.bottom() - 34, 320, 26)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(9, 35, 17, 195))
        painter.drawRoundedRect(hud_rect, 6, 6)
        painter.setPen(QColor("#D5F5D8"))
        painter.setFont(QFont("Consolas", 9))
        hud_text = (
            f"MODEL:{self._info['model']}  CAM:{self._info['cam']}  "
            f"OBJ:{self._info['objects']}  FPS:{self._info['fps']}"
        )
        painter.drawText(hud_rect.adjusted(8, 0, -8, 0), Qt.AlignVCenter, hud_text)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 920)
        MainWindow.setWindowTitle("Meta Farm")

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet(
            """
            QWidget {
                background: #FAFAF5;
                color: #1B3C1D;
                font-family: "Segoe UI", "Microsoft YaHei";
            }
            QLabel[class="section_title"] {
                color: #1B3C1D;
                font-size: 17px;
                font-weight: 700;
            }
            QComboBox, QLineEdit, QTextEdit, QSpinBox {
                background: #FFFFFF;
                border: 1px solid #D8E2D3;
                border-radius: 9px;
                padding: 6px 8px;
            }
            QListWidget {
                background: #FFFFFF;
                border: 1px solid #D8E2D3;
                border-radius: 12px;
            }
            """
        )
        MainWindow.setCentralWidget(self.centralwidget)

        root = QVBoxLayout(self.centralwidget)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)

        header = HoverCard()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 12, 18, 12)
        header_layout.setSpacing(10)

        title = QLabel("Meta Farm 智慧养殖中台")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1B3C1D;")
        subtitle = QLabel("Forest Green Console")
        subtitle.setStyleSheet("font-size: 12px; color: #739574;")
        title_col = QVBoxLayout()
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header_layout.addLayout(title_col)
        header_layout.addStretch(1)

        self.nav_buttons = []
        self.nav_group = QButtonGroup(MainWindow)
        nav_titles = ["农场首页", "农场监控", "我的认养", "订阅订单", "个人中心"]
        for i, name in enumerate(nav_titles):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(36)
            btn.setStyleSheet(
                """
                QPushButton {
                    border: 1px solid #C7D8C2;
                    border-radius: 10px;
                    background: #FFFFFF;
                    color: #2F4D30;
                    padding: 7px 12px;
                    font-weight: 600;
                }
                QPushButton:hover { border-color: #7FAE81; }
                QPushButton:checked {
                    background: #2E7D32;
                    color: #FAFAF5;
                    border-color: #2E7D32;
                }
                """
            )
            self.nav_group.addButton(btn, i)
            header_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        self.pushButton_5 = QPushButton("关闭")
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setCursor(Qt.PointingHandCursor)
        self.pushButton_5.setStyleSheet(
            "QPushButton { border: none; color: #C62828; font-weight: 700; padding: 6px 10px; }"
            "QPushButton:hover { background: #FBE9E9; border-radius: 8px; }"
        )
        header_layout.addWidget(self.pushButton_5)
        root.addWidget(header)

        self.pages = QStackedWidget()
        root.addWidget(self.pages, 1)

        self.page_home = self._build_page_home()
        self.page_monitor = self._build_page_monitor()
        self.page_adopt = self._build_page_adopt()
        self.page_order = self._build_page_order()
        self.page_profile = self._build_page_profile()

        for p in [self.page_home, self.page_monitor, self.page_adopt, self.page_order, self.page_profile]:
            self.pages.addWidget(p)

        self.nav_group.idClicked.connect(self.pages.setCurrentIndex)
        self.nav_buttons[0].setChecked(True)

        self.retranslateUi(MainWindow)
        self.pushButton_5.clicked.connect(MainWindow.close)
        QMetaObject.connectSlotsByName(MainWindow)

    def _section_label(self, text):
        label = QLabel(text)
        label.setProperty("class", "section_title")
        return label

    def _build_page_home(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setSpacing(12)

        hero = QFrame()
        hero.setMinimumHeight(180)
        hero.setStyleSheet(
            """
            QFrame {
                border-radius: 16px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2E7D32, stop:0.6 #5D8E5F, stop:1 #D7CCC8);
            }
            """
        )
        hero_l = QHBoxLayout(hero)
        hero_l.setContentsMargins(22, 18, 22, 18)
        hero_text = QVBoxLayout()
        h1 = QLabel("今日牧场概览")
        h1.setStyleSheet("font-size: 28px; color: #FAFAF5; font-weight: 800;")
        h2 = QLabel("蛋鸡状态稳定，建议 16:00 前完成饲料补给")
        h2.setStyleSheet("font-size: 14px; color: #F3FBEF;")
        hero_text.addWidget(h1)
        hero_text.addWidget(h2)
        hero_text.addStretch(1)
        hero_l.addLayout(hero_text)
        hero_l.addStretch(1)
        yolo_badge = YoloIndicator("YOLOv11n 在线巡检", active=True)
        yolo_badge.setStyleSheet("background: transparent;")
        hero_l.addWidget(yolo_badge)
        lay.addWidget(hero)

        lay.addWidget(self._section_label("3 大快捷卡"))
        quick_row = QHBoxLayout()
        for title, desc in [
            ("开始巡检", "一键切换到实时监控并启动相机"),
            ("生成日报", "自动汇总产蛋、异常和温湿度趋势"),
            ("通知认养人", "将异常动态推送到订阅用户"),
        ]:
            card = HoverCard()
            c_lay = QVBoxLayout(card)
            c_lay.addWidget(QLabel(f"<b>{title}</b>"))
            d = QLabel(desc)
            d.setStyleSheet("color:#5F6F58;")
            d.setWordWrap(True)
            c_lay.addWidget(d)
            c_lay.addStretch(1)
            go = GreenButton("立即执行")
            c_lay.addWidget(go)
            quick_row.addWidget(card)
        lay.addLayout(quick_row)

        lay.addWidget(self._section_label("5 统计卡"))
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        cards = [
            ("在线摄像头", "4 路", "全部正常"),
            ("今日产蛋", "245 枚", "+12% 较昨日"),
            ("实时告警", "3 条", "2 条待处理"),
            ("认养会员", "186 人", "本月 +23"),
            ("饲料库存", "72%", "可用 8 天"),
        ]
        for t, v, tip in cards:
            stats_row.addWidget(StatCard(t, v, tip))
        lay.addLayout(stats_row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)

        activity = HoverCard()
        a_lay = QVBoxLayout(activity)
        a_lay.addWidget(self._section_label("活动流"))
        for msg in [
            "08:12 CAM-02 检测到采食下降 11%",
            "09:40 自动补光策略已开启",
            "11:06 会员 YH-093 查看了溯源凭证",
            "12:31 订阅订单 HK-20260316 已发货",
            "14:02 产蛋效率达到今日峰值",
        ]:
            label = QLabel(f"• {msg}")
            label.setStyleSheet("color: #375539;")
            a_lay.addWidget(label)
        a_lay.addStretch(1)

        eggs = HoverCard()
        e_lay = QVBoxLayout(eggs)
        e_lay.addWidget(self._section_label("产蛋柱状图"))
        e_lay.addWidget(MiniBarChart([26, 32, 35, 38, 42, 40, 45]))

        grid.addWidget(activity, 0, 0)
        grid.addWidget(eggs, 0, 1)
        lay.addLayout(grid)
        return page

    def _build_page_monitor(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setSpacing(10)

        control_card = HoverCard()
        ctrl = QHBoxLayout(control_card)
        ctrl.setContentsMargins(14, 10, 14, 10)
        ctrl.setSpacing(8)

        self.pushButton = GreenButton("上传图片")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = GreenButton("上传视频")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = GreenButton("打开摄像头")
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = GreenButton("停止视频/摄像头")
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setEnabled(False)
        self.yolo_indicator = YoloIndicator("YOLOv11n 推理中", active=True)

        for w in [self.pushButton, self.pushButton_2, self.pushButton_3, self.pushButton_4]:
            ctrl.addWidget(w)
        ctrl.addSpacing(8)
        ctrl.addWidget(self.yolo_indicator, 1)
        lay.addWidget(control_card)

        body = QHBoxLayout()
        body.setSpacing(10)

        left = QVBoxLayout()
        canvas_card = HoverCard()
        c_lay = QVBoxLayout(canvas_card)
        c_lay.addWidget(self._section_label("YoloCanvas 实时检测"))
        self.label_3 = YoloCanvas()
        self.label_3.setObjectName("label_3")
        c_lay.addWidget(self.label_3)
        body.addLayout(left, 2)
        left.addWidget(canvas_card)

        cameras = HoverCard()
        cam_lay = QHBoxLayout(cameras)
        cam_lay.addWidget(QLabel("4 路摄像头切换"))
        self.cam_group = QButtonGroup(page)
        for i in range(1, 5):
            cam_btn = QPushButton(f"CAM-{i:02d}")
            cam_btn.setCheckable(True)
            cam_btn.setCursor(Qt.PointingHandCursor)
            cam_btn.setStyleSheet(
                "QPushButton { background:#FFFFFF; border:1px solid #C7D8C2; border-radius:8px; padding:6px 10px;}"
                "QPushButton:checked { background:#2E7D32; color:#FAFAF5; border-color:#2E7D32;}"
            )
            self.cam_group.addButton(cam_btn, i)
            cam_lay.addWidget(cam_btn)
            if i == 1:
                cam_btn.setChecked(True)
        cam_lay.addStretch(1)
        left.addWidget(cameras)

        right = QVBoxLayout()
        env = HoverCard()
        env_lay = QVBoxLayout(env)
        env_lay.addWidget(self._section_label("环境仪表板"))
        donuts = QHBoxLayout()
        donuts.addWidget(DonutWidget(87, "通风指数"))
        donuts.addWidget(DonutWidget(72, "温湿稳定"))
        env_lay.addLayout(donuts)
        right.addWidget(env)

        alerts = HoverCard()
        al = QVBoxLayout(alerts)
        al.addWidget(self._section_label("异常告警"))
        for text, color in [
            ("高优先级: CAM-03 检测到长时间扎堆", "#C62828"),
            ("中优先级: 饮水线流速偏低", "#EF6C00"),
            ("低优先级: 夜间噪声略高", "#607D8B"),
        ]:
            item = QLabel(text)
            item.setStyleSheet(f"color:{color}; font-weight:600;")
            al.addWidget(item)
        al.addStretch(1)
        right.addWidget(alerts)

        inspect = HoverCard()
        ins = QGridLayout(inspect)
        ins.setHorizontalSpacing(8)
        ins.setVerticalSpacing(6)

        self.label_4 = QLabel("耗时")
        self.label_6 = QLabel("-")
        self.label_10 = QLabel("目标数量")
        self.label_11 = QLabel("0")
        self.label_14 = QLabel("置信度")
        self.label_15 = QLabel("-")
        self.label_17 = QLabel("类别")
        self.label_16 = QLabel("-")
        self.label_12 = QLabel("xmin")
        self.label_13 = QLabel("-")
        self.label_20 = QLabel("ymin")
        self.label_19 = QLabel("-")
        self.label_22 = QLabel("xmax")
        self.label_21 = QLabel("-")
        self.label_24 = QLabel("ymax")
        self.label_23 = QLabel("-")
        self.label_18 = QLabel("对象选择")
        self.comboBox = QComboBox()
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("全部")

        rows = [
            (self.label_4, self.label_6, self.label_10, self.label_11),
            (self.label_14, self.label_15, self.label_17, self.label_16),
            (self.label_12, self.label_13, self.label_20, self.label_19),
            (self.label_22, self.label_21, self.label_24, self.label_23),
        ]
        for r, line in enumerate(rows):
            ins.addWidget(line[0], r, 0)
            ins.addWidget(line[1], r, 1)
            ins.addWidget(line[2], r, 2)
            ins.addWidget(line[3], r, 3)
        ins.addWidget(self.label_18, 4, 0)
        ins.addWidget(self.comboBox, 4, 1, 1, 3)

        right.addWidget(inspect)

        body.addLayout(right, 1)
        lay.addLayout(body)
        return page

    def _build_page_adopt(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setSpacing(10)

        list_card = HoverCard()
        left = QVBoxLayout(list_card)
        left.addWidget(self._section_label("我的认养鸡只"))
        self.chicken_list = QListWidget()
        for idx, name in enumerate(["小麦", "青禾", "阿栗", "暖暖", "元宝", "柚子"], start=1):
            item = QListWidgetItem(self.chicken_list)
            item.setSizeHint(QRectF(0, 0, 260, 60).size().toSize())
            row = QWidget()
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(8, 6, 8, 6)
            row_lay.addWidget(ChickenAvatar(f"{idx}"))
            txt = QVBoxLayout()
            txt.addWidget(QLabel(f"{name} · CHK-{100+idx}"))
            sub = QLabel("状态: 健康  |  最近产蛋: 14:25")
            sub.setStyleSheet("color:#5F6F58; font-size:12px;")
            txt.addWidget(sub)
            row_lay.addLayout(txt)
            self.chicken_list.setItemWidget(item, row)
        left.addWidget(self.chicken_list)
        jump_btn = GreenButton("跳转农场监控")
        jump_btn.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        left.addWidget(jump_btn)

        detail = HoverCard()
        right = QVBoxLayout(detail)
        right.addWidget(self._section_label("详情面板"))
        right.addWidget(QLabel("饲料配方"))
        feed = QTextEdit("玉米 45%\n豆粕 21%\n贝壳粉 8%\n功能添加剂 2%")
        feed.setMaximumHeight(90)
        right.addWidget(feed)

        right.addWidget(QLabel("日志"))
        logs = QTextEdit("09:00 采食正常\n12:15 体态稳定\n14:40 巡检无异常")
        logs.setMaximumHeight(110)
        right.addWidget(logs)

        right.addWidget(QLabel("YOLO 实时数据"))
        yolo_data = QGridLayout()
        yolo_data.addWidget(StatCard("动作识别", "觅食", "持续 3m 20s"), 0, 0)
        yolo_data.addWidget(StatCard("活跃度", "81", "较平均 +7"), 0, 1)
        yolo_data.addWidget(StatCard("健康评分", "A", "羽毛与步态正常"), 1, 0)
        yolo_data.addWidget(StatCard("异常次数", "0", "近 24h"), 1, 1)
        right.addLayout(yolo_data)

        lay.addWidget(list_card, 1)
        lay.addWidget(detail, 2)
        return page

    def _build_page_order(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setSpacing(10)

        left = HoverCard()
        left_lay = QVBoxLayout(left)
        left_lay.addWidget(self._section_label("订阅订单"))

        order_scroll = QScrollArea()
        order_scroll.setWidgetResizable(True)
        order_scroll.setStyleSheet("border:none;")
        order_wrap = QWidget()
        wrap_lay = QVBoxLayout(order_wrap)
        wrap_lay.setSpacing(8)
        for oid, status, eggs in [
            ("HK-20260316-001", "配送中", "30 枚/月"),
            ("HK-20260316-002", "待支付", "60 枚/月"),
            ("HK-20260316-003", "已完成", "30 枚/月"),
        ]:
            card = HoverCard()
            cl = QVBoxLayout(card)
            cl.addWidget(QLabel(f"<b>{oid}</b>"))
            cl.addWidget(QLabel(f"订阅规格: {eggs}"))
            st = QLabel(f"订单状态: {status}")
            st.setStyleSheet("color:#5F6F58;")
            cl.addWidget(st)
            btn = QPushButton("查看溯源凭证")
            btn.clicked.connect(self._show_trace_dialog)
            btn.setStyleSheet("QPushButton { color:#2E7D32; border:none; font-weight:700; text-align:left; }")
            cl.addWidget(btn)
            wrap_lay.addWidget(card)
        wrap_lay.addStretch(1)
        order_scroll.setWidget(order_wrap)
        left_lay.addWidget(order_scroll)

        right = HoverCard()
        right_lay = QVBoxLayout(right)
        right_lay.addWidget(self._section_label("配送设置"))
        right_lay.addWidget(QLabel("收货地区"))
        region = QComboBox()
        region.addItems(["香港岛", "九龙", "新界"])
        right_lay.addWidget(region)
        right_lay.addWidget(QLabel("配送时段"))
        slot = QComboBox()
        slot.addItems(["09:00 - 12:00", "14:00 - 18:00", "18:00 - 21:00"])
        right_lay.addWidget(slot)
        right_lay.addWidget(QLabel("详细地址"))
        right_lay.addWidget(QLineEdit())

        right_lay.addSpacing(8)
        right_lay.addWidget(self._section_label("香港支付"))
        octopus = QRadioButton("八达通")
        alipay_hk = QRadioButton("支付宝 HK")
        octopus.setChecked(True)
        right_lay.addWidget(octopus)
        right_lay.addWidget(alipay_hk)
        right_lay.addSpacing(8)
        right_lay.addWidget(GreenButton("确认支付"))
        right_lay.addStretch(1)

        lay.addWidget(left, 2)
        lay.addWidget(right, 1)
        return page

    def _build_page_profile(self):
        page = QWidget()
        lay = QGridLayout(page)
        lay.setHorizontalSpacing(10)
        lay.setVerticalSpacing(10)

        mem = HoverCard()
        m = QVBoxLayout(mem)
        m.addWidget(self._section_label("个人中心"))
        m.addWidget(QLabel("会员等级: Forest Plus"))
        m.addWidget(QLabel("到期时间: 2026-08-30"))
        renew = GreenButton("会员续费")
        renew.clicked.connect(self._show_renew_dialog)
        m.addWidget(renew)
        m.addStretch(1)

        faq = HoverCard()
        f = QVBoxLayout(faq)
        f.addWidget(self._section_label("帮助 FAQ"))
        box = QToolBox()
        for q, a in [
            ("如何查看 YOLO 识别日志？", "进入农场监控页，右侧可查看实时目标及坐标。"),
            ("如何下载溯源凭证？", "在订阅订单页点击查看溯源凭证，弹窗内可导出。"),
            ("认养鸡只可以更换吗？", "可在每月结算后申请更换，系统 24h 内处理。"),
        ]:
            panel = QWidget()
            pl = QVBoxLayout(panel)
            txt = QLabel(a)
            txt.setWordWrap(True)
            pl.addWidget(txt)
            box.addItem(panel, q)
        f.addWidget(box)

        feedback = HoverCard()
        fb = QVBoxLayout(feedback)
        fb.addWidget(self._section_label("反馈中心"))
        fb.addWidget(QLabel("问题描述"))
        self.feedback_edit = QTextEdit()
        self.feedback_edit.setPlaceholderText("可描述模型误检、漏检或配送问题...")
        fb.addWidget(self.feedback_edit)
        upload = QPushButton("上传 YOLO 截图")
        upload.clicked.connect(self._choose_feedback_image)
        upload.setCursor(Qt.PointingHandCursor)
        upload.setStyleSheet(
            "QPushButton { border:1px dashed #7FAE81; border-radius:8px; background:#FFFFFF; padding:8px; }"
            "QPushButton:hover { background:#F3FAEE; }"
        )
        self.feedback_file = QLabel("未上传文件")
        self.feedback_file.setStyleSheet("color:#5F6F58;")
        fb.addWidget(upload)
        fb.addWidget(self.feedback_file)
        fb.addWidget(GreenButton("提交反馈"))

        notice = HoverCard()
        n = QVBoxLayout(notice)
        n.addWidget(self._section_label("通知设置"))
        n.addWidget(QCheckBox("异常告警推送"))
        n.addWidget(QCheckBox("订单配送推送"))
        n.addWidget(QCheckBox("会员到期提醒"))
        n.addWidget(QCheckBox("每周运营周报"))
        n.addWidget(QLabel("静默时段"))
        quiet = QHBoxLayout()
        quiet.addWidget(QSpinBox())
        quiet.addWidget(QLabel("至"))
        quiet.addWidget(QSpinBox())
        n.addLayout(quiet)
        n.addStretch(1)

        lay.addWidget(mem, 0, 0)
        lay.addWidget(faq, 0, 1)
        lay.addWidget(feedback, 1, 0)
        lay.addWidget(notice, 1, 1)
        return page

    def _show_trace_dialog(self):
        dialog = QDialog()
        dialog.setWindowTitle("溯源凭证")
        dialog.resize(460, 320)
        dialog.setStyleSheet("background:#FAFAF5;")
        lay = QVBoxLayout(dialog)
        lay.addWidget(QLabel("<b>批次号:</b> TRACE-20260316-CHICKEN-A"))
        lay.addWidget(QLabel("<b>饲养场:</b> 元朗智慧农场"))
        lay.addWidget(QLabel("<b>饲料批次:</b> FEED-HK-8821"))
        lay.addWidget(QLabel("<b>YOLO 巡检摘要:</b> 通过，近 7 日异常率 1.2%"))
        lay.addStretch(1)
        lay.addWidget(GreenButton("导出凭证 PDF"))
        dialog.exec()

    def _show_renew_dialog(self):
        dialog = QDialog()
        dialog.setWindowTitle("会员续费")
        dialog.resize(380, 260)
        dialog.setStyleSheet("background:#FAFAF5;")
        lay = QVBoxLayout(dialog)
        lay.addWidget(QLabel("Forest Plus 续费方案"))
        lay.addWidget(QLabel("1 个月: HKD 88"))
        lay.addWidget(QLabel("6 个月: HKD 468"))
        lay.addWidget(QLabel("12 个月: HKD 888"))
        lay.addStretch(1)
        lay.addWidget(GreenButton("确认续费"))
        dialog.exec()

    def _choose_feedback_image(self):
        file_name, _ = QFileDialog.getOpenFileName(None, "选择截图", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.feedback_file.setText(file_name)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Meta Farm", None))
