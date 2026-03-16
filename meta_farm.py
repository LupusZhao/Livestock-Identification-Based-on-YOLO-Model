"""
Meta Farm - PySide6 Desktop Application
基于YOLO鸡只识别的智慧农场管理平台
"""

import sys
import os
import random
import math
import time
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QStackedWidget,
    QGridLayout, QProgressBar, QLineEdit, QComboBox, QTextEdit,
    QDialog, QGraphicsDropShadowEffect, QSizePolicy, QSpacerItem,
    QSlider, QCheckBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QGroupBox
)
from PySide6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect,
    Signal, QThread, QSize, QPoint, QObject, QEvent
)
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient,
    QFont, QFontDatabase, QPixmap, QPainterPath, QIcon, QCursor, QImage,
    QKeySequence, QShortcut, QPalette, QPolygon, QConicalGradient
)

try:
    import cv2
    import numpy as np
    from ultralytics import YOLO
except Exception:
    cv2 = None
    np = None
    YOLO = None


# ─────────────────────────────────────────────
#  GLOBAL DESIGN TOKENS
# ─────────────────────────────────────────────
class Theme:
    # Colors
    PRIMARY       = "#2E7D32"
    PRIMARY_DARK  = "#1B5E20"
    PRIMARY_LIGHT = "#4CAF50"
    PRIMARY_PALE  = "#E8F5E9"
    ACCENT        = "#8BC34A"

    WOOD          = "#D7CCC8"
    WOOD_DARK     = "#BCAAA4"
    WOOD_LIGHT    = "#EFEBE9"

    BG            = "#FAFAF5"
    BG_CARD       = "#FFFFFF"
    BG_NAV        = "#1A3A1C"
    BG_NAV_HOVER  = "#2E7D32"

    TEXT_PRIMARY  = "#1C2B1E"
    TEXT_SECONDARY= "#5D7A60"
    TEXT_MUTED    = "#9DB09F"
    TEXT_WHITE    = "#FFFFFF"

    BORDER        = "#E0E8E0"
    SHADOW        = "rgba(46,125,50,0.12)"

    WARNING       = "#FF8F00"
    ERROR         = "#C62828"
    SUCCESS       = "#2E7D32"
    INFO          = "#0277BD"

    GOLD          = "#F9A825"

    # Typography
    FONT_DISPLAY  = "Georgia"
    FONT_BODY     = "PingFang SC"
    FONT_MONO     = "SF Mono"

    # Sizes
    RADIUS_SM     = "6px"
    RADIUS_MD     = "10px"
    RADIUS_LG     = "16px"
    RADIUS_XL     = "24px"

    NAV_WIDTH     = 200
    TOPBAR_H      = 56
    CONTENT_PAD   = 24


# ─────────────────────────────────────────────
#  MOCK DATA
# ─────────────────────────────────────────────
MOCK_CHICKENS = [
    {"id":"C001","name":"小金","breed":"芦花鸡","age":142,"weight":2.3,"health":98,"eggs_total":87,"status":"健康","location":"A区-3号","img_color":"#F9A825"},
    {"id":"C002","name":"珍珠","breed":"乌骨鸡","age":98, "weight":1.9,"health":92,"eggs_total":54,"status":"健康","location":"A区-5号","img_color":"#795548"},
    {"id":"C003","name":"阿福","breed":"清远麻鸡","age":203,"weight":2.6,"health":76,"eggs_total":112,"status":"需关注","location":"B区-1号","img_color":"#8D6E63"},
    {"id":"C004","name":"白雪","breed":"白来航","age":67, "weight":1.7,"health":95,"eggs_total":31,"status":"健康","location":"B区-4号","img_color":"#EEEEEE"},
    {"id":"C005","name":"黑旋风","breed":"黑羽鸡","age":178,"weight":2.4,"health":88,"eggs_total":93,"status":"健康","location":"C区-2号","img_color":"#424242"},
    {"id":"C006","name":"芝麻","breed":"麻鸡","age":55, "weight":1.5,"health":91,"eggs_total":18,"status":"健康","location":"C区-6号","img_color":"#A1887F"},
]

MOCK_ORDERS = [
    {"id":"ORD-2025-001","plan":"有机鸡蛋月度套餐","qty":"30枚/月","price":"HK$280","status":"配送中","date":"2025-07-01","next":"2025-08-01","address":"九龍塘德雅道15號","trace":"TRC-A2025-07"},
    {"id":"ORD-2025-002","plan":"走地鸡季度套餐","qty":"1只/季","price":"HK$680","status":"待配送","date":"2025-07-15","next":"2025-10-15","address":"中環皇后大道中100號","trace":"TRC-B2025-07"},
    {"id":"ORD-2024-018","plan":"有机鸡蛋月度套餐","qty":"30枚/月","price":"HK$280","status":"已完成","date":"2025-06-01","next":"—","address":"九龍塘德雅道15號","trace":"TRC-A2025-06"},
]

MOCK_LOGS = [
    {"date":"2025-07-18 09:23","event":"YOLO识别：体重估算 2.31kg","type":"ai","chicken":"C001"},
    {"date":"2025-07-18 08:00","event":"产蛋记录：发现新蛋 1枚","type":"egg","chicken":"C001"},
    {"date":"2025-07-17 14:55","event":"YOLO识别：行为正常，活动频率高","type":"ai","chicken":"C001"},
    {"date":"2025-07-17 09:00","event":"饲料更换：有机玉米 + 豆粕配方","type":"feed","chicken":"C001"},
    {"date":"2025-07-16 10:30","event":"健康检查：体温 41.2°C（正常）","type":"health","chicken":"C001"},
    {"date":"2025-07-15 08:15","event":"YOLO识别：羽毛光泽度良好","type":"ai","chicken":"C001"},
]

MOCK_ENV = {
    "temp": 24.5, "humidity": 68, "co2": 420,
    "light": 850, "ammonia": 12, "wind": 0.8
}


# ─────────────────────────────────────────────
#  UTILITY WIDGETS
# ─────────────────────────────────────────────
def shadow(widget, blur=20, color="#2E7D32", opacity=0.15, offset=(0,4)):
    eff = QGraphicsDropShadowEffect()
    c = QColor(color)
    c.setAlphaF(opacity)
    eff.setColor(c)
    eff.setBlurRadius(blur)
    eff.setOffset(*offset)
    widget.setGraphicsEffect(eff)
    return eff


class HoverCard(QFrame):
    clicked = Signal()

    def __init__(self, parent=None, radius=12, bg="#FFFFFF", hover_bg=None):
        super().__init__(parent)
        self._bg = bg
        self._hover_bg = hover_bg or bg
        self._radius = radius
        self._hovered = False
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(f"""
            HoverCard {{
                background:{bg};
                border-radius:{radius}px;
                border:1.5px solid {Theme.BORDER};
            }}
        """)
        shadow(self, 12, Theme.PRIMARY, 0.08)

    def enterEvent(self, e):
        self._hovered = True
        self.setStyleSheet(f"""
            HoverCard {{
                background:{self._hover_bg};
                border-radius:{self._radius}px;
                border:1.5px solid {Theme.PRIMARY_LIGHT};
            }}
        """)
        shadow(self, 24, Theme.PRIMARY, 0.18, (0,8))
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False
        self.setStyleSheet(f"""
            HoverCard {{
                background:{self._bg};
                border-radius:{self._radius}px;
                border:1.5px solid {Theme.BORDER};
            }}
        """)
        shadow(self, 12, Theme.PRIMARY, 0.08)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)


class GreenButton(QPushButton):
    def __init__(self, text, parent=None, small=False, outlined=False):
        super().__init__(text, parent)
        h = "32px" if small else "42px"
        pad = "0 16px" if small else "0 24px"
        fs = "13px" if small else "14px"

        if outlined:
            self.setStyleSheet(f"""
                QPushButton {{
                    background:transparent;
                    color:{Theme.PRIMARY};
                    border:2px solid {Theme.PRIMARY};
                    border-radius:8px;
                    height:{h};
                    padding:{pad};
                    font-size:{fs};
                    font-weight:600;
                    font-family:'{Theme.FONT_BODY}';
                }}
                QPushButton:hover {{
                    background:{Theme.PRIMARY_PALE};
                    border-color:{Theme.PRIMARY_DARK};
                }}
                QPushButton:pressed {{ background:{Theme.PRIMARY_PALE}; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                        stop:0 {Theme.PRIMARY_LIGHT}, stop:1 {Theme.PRIMARY});
                    color:white;
                    border:none;
                    border-radius:8px;
                    height:{h};
                    padding:{pad};
                    font-size:{fs};
                    font-weight:600;
                    font-family:'{Theme.FONT_BODY}';
                }}
                QPushButton:hover {{
                    background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                        stop:0 {Theme.PRIMARY}, stop:1 {Theme.PRIMARY_DARK});
                }}
                QPushButton:pressed {{ background:{Theme.PRIMARY_DARK}; }}
            """)
        self.setCursor(QCursor(Qt.PointingHandCursor))


class SectionTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            font-size:20px; font-weight:700;
            color:{Theme.TEXT_PRIMARY};
            font-family:'{Theme.FONT_DISPLAY}';
            padding-bottom:4px;
            border-bottom:3px solid {Theme.PRIMARY};
        """)


class Badge(QLabel):
    def __init__(self, text, color=Theme.SUCCESS, parent=None):
        super().__init__(f"  {text}  ", parent)
        self.setStyleSheet(f"""
            background:{color}22;
            color:{color};
            border:1px solid {color}55;
            border-radius:10px;
            font-size:11px;
            font-weight:600;
            padding:2px 0;
            font-family:'{Theme.FONT_BODY}';
        """)
        self.setFixedHeight(20)


class StatCard(HoverCard):
    def __init__(self, icon, value, label, trend=None, color=Theme.PRIMARY, parent=None):
        super().__init__(parent, 12)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(6)

        top = QHBoxLayout()
        ico = QLabel(icon)
        ico.setStyleSheet(f"font-size:22px; background:{color}18; border-radius:10px; padding:6px;")
        ico.setFixedSize(44, 44)
        ico.setAlignment(Qt.AlignCenter)
        top.addWidget(ico)
        top.addStretch()
        if trend:
            t_color = Theme.SUCCESS if trend.startswith("+") else Theme.ERROR
            tl = QLabel(trend)
            tl.setStyleSheet(f"color:{t_color}; font-size:12px; font-weight:600;")
            top.addWidget(tl)
        lay.addLayout(top)

        vl = QLabel(value)
        vl.setStyleSheet(f"font-size:26px; font-weight:700; color:{color}; font-family:'{Theme.FONT_DISPLAY}';")
        lay.addWidget(vl)

        ll = QLabel(label)
        ll.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_SECONDARY};")
        lay.addWidget(ll)

        self.setFixedHeight(130)


class ChickenAvatar(QWidget):
    def __init__(self, color="#F9A825", size=60, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(size, size)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(self.color)
        # body
        p.setBrush(QBrush(c))
        p.setPen(Qt.NoPen)
        p.drawEllipse(4, 14, self.width()-8, self.height()-18)
        # head
        p.drawEllipse(self.width()//2-12, 2, 24, 24)
        # beak
        p.setBrush(QBrush(QColor("#FF8F00")))
        pts = [QPoint(self.width()//2+11, 10), QPoint(self.width()//2+20, 14), QPoint(self.width()//2+11, 18)]
        p.drawPolygon(QPolygon(pts))
        # eye
        p.setBrush(QBrush(QColor("#212121")))
        p.drawEllipse(self.width()//2+2, 7, 5, 5)
        p.setBrush(QBrush(QColor("white")))
        p.drawEllipse(self.width()//2+3, 7, 2, 2)
        # comb
        p.setBrush(QBrush(QColor("#C62828")))
        for i in range(3):
            p.drawEllipse(self.width()//2-4+i*5, 0, 6, 8)
        p.end()


class DonutWidget(QWidget):
    def __init__(self, value=75, label="", color=Theme.PRIMARY, parent=None):
        super().__init__(parent)
        self.value = value
        self.label = label
        self.color = color
        self.setFixedSize(90, 90)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRect(8, 8, 74, 74)
        # bg arc
        p.setPen(QPen(QColor(Theme.BORDER), 8, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(r, 0, 360*16)
        # value arc
        p.setPen(QPen(QColor(self.color), 8, Qt.SolidLine, Qt.RoundCap))
        angle = int(self.value / 100 * 360 * 16)
        p.drawArc(r, 90*16, -angle)
        # text
        p.setPen(QColor(Theme.TEXT_PRIMARY))
        p.setFont(QFont(Theme.FONT_DISPLAY, 14, QFont.Bold))
        p.drawText(r, Qt.AlignCenter, f"{self.value}%")
        p.end()


class MiniBarChart(QWidget):
    def __init__(self, data, color=Theme.PRIMARY, parent=None):
        super().__init__(parent)
        self.data = data
        self.color = color
        self.setFixedHeight(60)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.data: return
        mx = max(self.data) or 1
        w = self.width()
        h = self.height()
        bw = max(6, w // len(self.data) - 4)
        gap = (w - bw * len(self.data)) // (len(self.data)+1)

        for i, v in enumerate(self.data):
            bh = int(v / mx * (h - 10))
            x = gap + i*(bw+gap)
            y = h - bh - 2
            p.setBrush(QBrush(QColor(self.color + "CC")))
            p.setPen(Qt.NoPen)
            path = QPainterPath()
            path.addRoundedRect(x, y, bw, bh, 3, 3)
            p.fillPath(path, QColor(self.color + "BB"))
        p.end()


class YoloIndicator(QWidget):
    """Pulsing YOLO active indicator"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._pulse = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def _tick(self):
        self._pulse = (self._pulse + 5) % 360
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        alpha = int(128 + 127 * math.sin(math.radians(self._pulse)))
        c = QColor(Theme.PRIMARY_LIGHT)
        c.setAlpha(alpha)
        p.setBrush(QBrush(c))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, 12, 12)
        p.end()


# ─────────────────────────────────────────────
#  YOLO MOCK ENGINE
# ─────────────────────────────────────────────
class YoloEngine(QObject):
    detectionUpdated = Signal(dict)

    def __init__(self):
        super().__init__()
        self._timer = QTimer()
        self._timer.timeout.connect(self._simulate)
        self._active = False
        self._frame = 0

    def start(self):
        self._active = True
        self._timer.start(1200)

    def stop(self):
        self._active = False
        self._timer.stop()

    def _simulate(self):
        self._frame += 1
        count = random.randint(3, 8)
        boxes = []
        for i in range(count):
            boxes.append({
                "id": f"chicken_{i+1}",
                "conf": round(random.uniform(0.82, 0.99), 2),
                "x": random.randint(10, 70),
                "y": random.randint(10, 70),
                "w": random.randint(8, 15),
                "h": random.randint(8, 15),
                "label": random.choice(["走地鸡","走地鸡","走地鸡","疑似异常"]),
            })
        self.detectionUpdated.emit({
            "frame": self._frame,
            "count": count,
            "boxes": boxes,
            "fps": round(random.uniform(24.5, 30.0), 1),
            "conf_avg": round(sum(b["conf"] for b in boxes)/count, 2),
            "anomaly": any(b["label"]=="疑似异常" for b in boxes),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })


# ─────────────────────────────────────────────
#  NAVIGATION BAR
# ─────────────────────────────────────────────
class NavItem(QWidget):
    clicked = Signal(int)

    def __init__(self, index, icon, label, parent=None):
        super().__init__(parent)
        self.index = index
        self._active = False
        self.setFixedHeight(52)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        self.indicator = QFrame()
        self.indicator.setFixedSize(3, 30)
        self.indicator.setStyleSheet("background:transparent; border-radius:2px;")
        lay.addWidget(self.indicator)

        self.ico_lbl = QLabel(icon)
        self.ico_lbl.setStyleSheet("font-size:18px; background:transparent;")
        self.ico_lbl.setFixedWidth(24)
        self.ico_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.ico_lbl)

        self.txt_lbl = QLabel(label)
        self.txt_lbl.setStyleSheet(f"font-size:14px; color:{Theme.WOOD}; font-family:'{Theme.FONT_BODY}'; background:transparent;")
        lay.addWidget(self.txt_lbl)
        lay.addStretch()

        self._update_style()

    def setActive(self, active):
        self._active = active
        self._update_style()

    def _update_style(self):
        if self._active:
            self.setStyleSheet(f"background:{Theme.BG_NAV_HOVER}; border-radius:10px;")
            self.indicator.setStyleSheet(f"background:{Theme.ACCENT}; border-radius:2px;")
            self.txt_lbl.setStyleSheet(f"font-size:14px; color:white; font-weight:600; font-family:'{Theme.FONT_BODY}'; background:transparent;")
        else:
            self.setStyleSheet("background:transparent; border-radius:10px;")
            self.indicator.setStyleSheet("background:transparent; border-radius:2px;")
            self.txt_lbl.setStyleSheet(f"font-size:14px; color:{Theme.WOOD}; font-family:'{Theme.FONT_BODY}'; background:transparent;")

    def enterEvent(self, e):
        if not self._active:
            self.setStyleSheet(f"background:{Theme.BG_NAV_HOVER}55; border-radius:10px;")
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._update_style()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(e)


class SideNav(QWidget):
    pageChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(Theme.NAV_WIDTH)
        self.setStyleSheet(f"background:{Theme.BG_NAV};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 0, 10, 20)
        lay.setSpacing(4)

        # Logo
        logo_frame = QFrame()
        logo_frame.setFixedHeight(80)
        logo_frame.setStyleSheet("background:transparent;")
        ll = QVBoxLayout(logo_frame)
        ll.setAlignment(Qt.AlignCenter)

        logo_txt = QLabel("🌿 Meta Farm")
        logo_txt.setStyleSheet(f"""
            font-size:16px; font-weight:700;
            color:white; font-family:'{Theme.FONT_DISPLAY}';
            background:transparent;
        """)
        logo_txt.setAlignment(Qt.AlignCenter)
        ll.addWidget(logo_txt)

        sub = QLabel("智慧農場管理平台")
        sub.setStyleSheet(f"font-size:10px; color:{Theme.WOOD}88; background:transparent;")
        sub.setAlignment(Qt.AlignCenter)
        ll.addWidget(sub)
        lay.addWidget(logo_frame)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background:{Theme.BG_NAV_HOVER};")
        lay.addWidget(div)
        lay.addSpacing(8)

        # Nav items
        nav_items = [
            ("🏡", "農場首頁"),
            ("📹", "農場監控"),
            ("🐔", "我的認養"),
            ("📦", "訂閱訂單"),
            ("👤", "個人中心"),
        ]
        self._items = []
        for i, (ico, lbl) in enumerate(nav_items):
            item = NavItem(i, ico, lbl)
            item.clicked.connect(self._on_nav_click)
            self._items.append(item)
            lay.addWidget(item)

        lay.addStretch()

        # Bottom status
        status_frame = QFrame()
        status_frame.setStyleSheet("background:transparent;")
        sl = QVBoxLayout(status_frame)
        sl.setSpacing(4)

        yolo_row = QHBoxLayout()
        yolo_dot = YoloIndicator()
        yolo_row.addWidget(yolo_dot)
        yolo_label = QLabel("YOLO 識別中")
        yolo_label.setStyleSheet(f"font-size:11px; color:{Theme.ACCENT}; background:transparent;")
        yolo_row.addWidget(yolo_label)
        yolo_row.addStretch()
        sl.addLayout(yolo_row)

        ver = QLabel("v2.4.1  ·  HK Edition")
        ver.setStyleSheet(f"font-size:10px; color:{Theme.WOOD}66; background:transparent;")
        sl.addWidget(ver)
        lay.addWidget(status_frame)

        self._items[0].setActive(True)
        self._current = 0

    def _on_nav_click(self, index):
        self._items[self._current].setActive(False)
        self._current = index
        self._items[index].setActive(True)
        self.pageChanged.emit(index)

    def navigate_to(self, index):
        self._on_nav_click(index)


# ─────────────────────────────────────────────
#  TOP STATUS BAR
# ─────────────────────────────────────────────
class TopBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(Theme.TOPBAR_H)
        self.setStyleSheet(f"""
            background:white;
            border-bottom:1px solid {Theme.BORDER};
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(0)

        # Breadcrumb / page title
        self.page_label = QLabel("農場首頁")
        self.page_label.setStyleSheet(f"""
            font-size:15px; font-weight:600;
            color:{Theme.TEXT_PRIMARY};
            font-family:'{Theme.FONT_BODY}';
        """)
        lay.addWidget(self.page_label)
        lay.addStretch()

        # Time
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"font-size:13px; color:{Theme.TEXT_MUTED};")
        lay.addWidget(self.time_label)
        lay.addSpacing(24)

        # Farm badge
        farm = QLabel("🏡  大嶼山生態農場")
        farm.setStyleSheet(f"""
            background:{Theme.PRIMARY_PALE};
            color:{Theme.PRIMARY_DARK};
            border-radius:6px;
            padding:4px 12px;
            font-size:12px; font-weight:600;
        """)
        lay.addWidget(farm)
        lay.addSpacing(16)

        # Notification
        notif = QPushButton("🔔")
        notif.setFixedSize(36, 36)
        notif.setStyleSheet(f"""
            QPushButton {{
                background:{Theme.BG};
                border:1px solid {Theme.BORDER};
                border-radius:18px;
                font-size:16px;
            }}
            QPushButton:hover {{ background:{Theme.PRIMARY_PALE}; }}
        """)
        notif.setCursor(QCursor(Qt.PointingHandCursor))
        lay.addWidget(notif)
        lay.addSpacing(12)

        # Avatar
        av = QLabel("陳")
        av.setFixedSize(36, 36)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {Theme.PRIMARY_LIGHT}, stop:1 {Theme.PRIMARY_DARK});
            color:white;
            border-radius:18px;
            font-size:14px; font-weight:700;
        """)
        lay.addWidget(av)

        self._tick()
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(1000)

    def _tick(self):
        self.time_label.setText(datetime.now().strftime("%Y年%m月%d日  %H:%M:%S"))

    def set_page(self, name):
        self.page_label.setText(name)


# ─────────────────────────────────────────────
#  PAGE 1: DASHBOARD
# ─────────────────────────────────────────────
class DashboardPage(QWidget):
    navigate = Signal(int)

    def __init__(self, yolo: YoloEngine, parent=None):
        super().__init__(parent)
        self.yolo = yolo
        self._carousel_idx = 0
        self._yolo_count = 0
        self._setup()
        yolo.detectionUpdated.connect(self._on_yolo)

    def _setup(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(Theme.CONTENT_PAD, Theme.CONTENT_PAD,
                                Theme.CONTENT_PAD, Theme.CONTENT_PAD)
        root.setSpacing(20)

        # ── Carousel Hero ─────────────────────
        hero = self._make_hero()
        root.addWidget(hero)

        # ── 3 Quick Cards ──────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        cards_row.addWidget(self._adoption_card())
        cards_row.addWidget(self._subscription_card())
        cards_row.addWidget(self._monitor_card())
        root.addLayout(cards_row)

        # ── Stats Row ─────────────────────────
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        self.stat_count = StatCard("🐔", str(self._yolo_count or 47), "今日識別鸡只", "+3", Theme.PRIMARY)
        stats_row.addWidget(self.stat_count)
        stats_row.addWidget(StatCard("🥚", "234", "本週產蛋量", "+12%", Theme.GOLD))
        stats_row.addWidget(StatCard("❤️", "94%", "群體健康指數", "+2%", Theme.SUCCESS))
        stats_row.addWidget(StatCard("🌡️", "24.5°C", "圍欄溫度", "正常", Theme.INFO))
        stats_row.addWidget(StatCard("💧", "68%", "環境濕度", "適宜", Theme.INFO))

        root.addLayout(stats_row)

        # ── Bottom Row ────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(16)
        bottom.addWidget(self._activity_panel(), 2)
        bottom.addWidget(self._egg_chart_panel(), 1)
        root.addLayout(bottom)

    def _make_hero(self):
        hero = QFrame()
        hero.setFixedHeight(180)
        hero.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {Theme.PRIMARY_DARK}, stop:0.5 {Theme.PRIMARY},
                stop:1 {Theme.PRIMARY_LIGHT});
            border-radius:16px;
        """)
        shadow(hero, 20, Theme.PRIMARY, 0.25)

        lay = QHBoxLayout(hero)
        lay.setContentsMargins(32, 24, 32, 24)

        left = QVBoxLayout()
        greeting = QLabel("早安，陳先生 👋")
        greeting.setStyleSheet("font-size:22px; font-weight:700; color:white; font-family:Georgia;")
        left.addWidget(greeting)

        sub = QLabel("您的農場今日運作一切正常，共有 6 隻認養雞只\n今日已產蛋 12 枚，環境指標良好")
        sub.setStyleSheet("font-size:13px; color:rgba(255,255,255,0.85); line-height:1.6;")
        sub.setWordWrap(True)
        left.addWidget(sub)
        left.addSpacing(12)

        btns = QHBoxLayout()
        b1 = QPushButton("▶  進入監控")
        b1.setStyleSheet("""
            QPushButton { background:white; color:#2E7D32; border:none; border-radius:8px;
                padding:8px 20px; font-size:13px; font-weight:700; }
            QPushButton:hover { background:#E8F5E9; }
        """)
        b1.setCursor(QCursor(Qt.PointingHandCursor))
        b1.clicked.connect(lambda: self.navigate.emit(1))
        btns.addWidget(b1)

        b2 = QPushButton("查看認養")
        b2.setStyleSheet("""
            QPushButton { background:rgba(255,255,255,0.2); color:white;
                border:1.5px solid rgba(255,255,255,0.5); border-radius:8px;
                padding:8px 20px; font-size:13px; font-weight:600; }
            QPushButton:hover { background:rgba(255,255,255,0.3); }
        """)
        b2.setCursor(QCursor(Qt.PointingHandCursor))
        b2.clicked.connect(lambda: self.navigate.emit(2))
        btns.addWidget(b2)
        btns.addStretch()
        left.addLayout(btns)

        lay.addLayout(left, 3)

        # Right: big chicken + YOLO badge
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignCenter)

        av = ChickenAvatar("#F9A825", 80)
        right.addWidget(av, 0, Qt.AlignCenter)

        self.yolo_hero_badge = QLabel("🤖 YOLO 識別中…")
        self.yolo_hero_badge.setStyleSheet("""
            background:rgba(255,255,255,0.2);
            color:white; border-radius:10px;
            padding:4px 12px; font-size:11px; font-weight:600;
        """)
        self.yolo_hero_badge.setAlignment(Qt.AlignCenter)
        right.addWidget(self.yolo_hero_badge)

        lay.addLayout(right, 1)
        return hero

    def _adoption_card(self):
        card = HoverCard(hover_bg=Theme.PRIMARY_PALE)
        card.clicked.connect(lambda: self.navigate.emit(2))
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(10)

        h = QHBoxLayout()
        h.addWidget(QLabel("🐔"))
        h.addStretch()
        b = Badge("6 隻在養", Theme.SUCCESS)
        h.addWidget(b)
        lay.addLayout(h)

        title = QLabel("我的認養")
        title.setStyleSheet(f"font-size:18px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        row = QHBoxLayout()
        for c in MOCK_CHICKENS[:3]:
            a = ChickenAvatar(c["img_color"], 32)
            row.addWidget(a)
        row.addStretch()
        lay.addLayout(row)

        sub = QLabel("小金、珍珠、阿福 等 6 隻")
        sub.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_SECONDARY};")
        lay.addWidget(sub)

        health_row = QHBoxLayout()
        health_row.addWidget(QLabel("健康狀態："))
        bar = QProgressBar()
        bar.setRange(0,100); bar.setValue(94)
        bar.setFixedHeight(8)
        bar.setStyleSheet(f"""
            QProgressBar {{ background:{Theme.BORDER}; border-radius:4px; }}
            QProgressBar::chunk {{ background:{Theme.SUCCESS}; border-radius:4px; }}
        """)
        bar.setTextVisible(False)
        health_row.addWidget(bar)
        health_row.addWidget(QLabel("94%"))
        lay.addLayout(health_row)

        return card

    def _subscription_card(self):
        card = HoverCard(hover_bg="#FFF8E1")
        card.clicked.connect(lambda: self.navigate.emit(3))
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(10)

        h = QHBoxLayout()
        h.addWidget(QLabel("📦"))
        h.addStretch()
        b = Badge("配送中", Theme.INFO)
        h.addWidget(b)
        lay.addLayout(h)

        title = QLabel("訂閱訂單")
        title.setStyleSheet(f"font-size:18px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        for o in MOCK_ORDERS[:2]:
            r = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{Theme.SUCCESS if o['status']=='配送中' else Theme.WOOD_DARK}; font-size:8px;")
            r.addWidget(dot)
            l = QLabel(o["plan"])
            l.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_PRIMARY};")
            r.addWidget(l)
            r.addStretch()
            s = QLabel(o["status"])
            s.setStyleSheet(f"font-size:11px; color:{Theme.TEXT_SECONDARY};")
            r.addWidget(s)
            lay.addLayout(r)

        nxt = QLabel(f"下次配送：2025-08-01")
        nxt.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_SECONDARY}; font-style:italic;")
        lay.addWidget(nxt)
        lay.addStretch()
        return card

    def _monitor_card(self):
        card = HoverCard(hover_bg="#E8F5E9")
        card.clicked.connect(lambda: self.navigate.emit(1))
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(10)

        h = QHBoxLayout()
        h.addWidget(QLabel("📹"))
        h.addStretch()
        b = Badge("直播中", Theme.ERROR)
        h.addWidget(b)
        lay.addLayout(h)

        title = QLabel("農場監控")
        title.setStyleSheet(f"font-size:18px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        # Mini YOLO view
        preview = QFrame()
        preview.setFixedHeight(70)
        preview.setStyleSheet(f"background:{Theme.BG_NAV}; border-radius:8px;")
        pl = QVBoxLayout(preview)
        pl.setAlignment(Qt.AlignCenter)
        self.yolo_preview = QLabel("🤖  YOLO 識別中  ·  47 隻")
        self.yolo_preview.setStyleSheet("color:#4CAF50; font-size:12px; font-weight:600;")
        self.yolo_preview.setAlignment(Qt.AlignCenter)
        pl.addWidget(self.yolo_preview)
        lay.addWidget(preview)

        enter = GreenButton("進入監控 →", small=True)
        enter.clicked.connect(lambda: self.navigate.emit(1))
        lay.addWidget(enter)
        return card

    def _activity_panel(self):
        card = HoverCard()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        title = QLabel("農場動態")
        title.setStyleSheet(f"font-size:16px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        events = [
            ("🥚", "09:23", "小金 產蛋 1 枚", Theme.GOLD),
            ("🤖", "09:10", "YOLO 識別：47 隻，健康指數 94%", Theme.PRIMARY),
            ("🌡️", "08:45", "圍欄溫度正常：24.5°C", Theme.INFO),
            ("⚠️", "08:30", "阿福 活動頻率偏低，請留意", Theme.WARNING),
            ("🥚", "08:15", "珍珠 產蛋 1 枚", Theme.GOLD),
            ("💊", "08:00", "定期健康監測完成", Theme.SUCCESS),
        ]
        for ico, t, msg, c in events:
            row = QHBoxLayout()
            dot = QLabel(ico)
            dot.setFixedWidth(24)
            row.addWidget(dot)
            time_l = QLabel(t)
            time_l.setStyleSheet(f"font-size:11px; color:{Theme.TEXT_MUTED}; min-width:40px;")
            row.addWidget(time_l)
            msg_l = QLabel(msg)
            msg_l.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_PRIMARY};")
            row.addWidget(msg_l)
            row.addStretch()
            lay.addLayout(row)

        return card

    def _egg_chart_panel(self):
        card = HoverCard()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        title = QLabel("本週產蛋")
        title.setStyleSheet(f"font-size:16px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        data = [28, 32, 35, 30, 38, 34, 37]
        chart = MiniBarChart(data, Theme.GOLD)
        lay.addWidget(chart)

        days = QHBoxLayout()
        for d in ["一","二","三","四","五","六","日"]:
            dl = QLabel(d)
            dl.setAlignment(Qt.AlignCenter)
            dl.setStyleSheet(f"font-size:10px; color:{Theme.TEXT_MUTED};")
            days.addWidget(dl)
        lay.addLayout(days)

        total = QLabel("本週合計：234 枚")
        total.setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.GOLD}; text-align:center;")
        total.setAlignment(Qt.AlignCenter)
        lay.addWidget(total)

        donuts = QHBoxLayout()
        for v, l, c in [(94,"健康",Theme.SUCCESS),(87,"產率",Theme.GOLD),(78,"活躍",Theme.INFO)]:
            dw = QVBoxLayout()
            d = DonutWidget(v, l, c)
            dw.addWidget(d, 0, Qt.AlignCenter)
            dl = QLabel(l)
            dl.setAlignment(Qt.AlignCenter)
            dl.setStyleSheet(f"font-size:10px; color:{Theme.TEXT_SECONDARY};")
            dw.addWidget(dl)
            donuts.addLayout(dw)
        lay.addLayout(donuts)

        return card

    def _on_yolo(self, data):
        self._yolo_count = data["count"]
        self.yolo_preview.setText(f"🤖  識別中  ·  {data['count']} 隻  ·  {data['fps']} fps")
        self.yolo_hero_badge.setText(f"🤖 YOLO ·  {data['count']} 隻  ·  {data['timestamp']}")
        if hasattr(self, 'stat_count'):
            # update value label
            for child in self.stat_count.findChildren(QLabel):
                if child.text().isdigit() or (len(child.text()) < 4 and child.text().replace('','').isdigit()):
                    pass


# ─────────────────────────────────────────────
#  PAGE 2: FARM MONITOR
# ─────────────────────────────────────────────
class YoloCanvas(QWidget):
    """YOLO detection overlay canvas"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = None
        self._boxes = []
        self._pixmap = None
        self.setMinimumHeight(360)

    def update_detection(self, data):
        self._data = data
        self._boxes = data.get("boxes", [])
        self.update()

    def update_frame(self, frame_bgr):
        if frame_bgr is None or cv2 is None:
            self._pixmap = None
            self.update()
            return
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, w * ch, QImage.Format_RGB888)
        self._pixmap = QPixmap.fromImage(qimg.copy())
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        if self._pixmap and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (w - scaled.width()) // 2
            y = (h - scaled.height()) // 2
            p.fillRect(0, 0, w, h, QColor("#0E1E10"))
            p.drawPixmap(x, y, scaled)
            p.end()
            return

        # Background: simulated farm scene
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor("#87CEEB"))
        grad.setColorAt(0.4, QColor("#87CEEB"))
        grad.setColorAt(0.4, QColor("#8FBC8F"))
        grad.setColorAt(1.0, QColor("#556B2F"))
        p.fillRect(0, 0, w, h, grad)

        # Ground
        ground = QPainterPath()
        ground.addRect(0, h*0.45, w, h*0.55)
        p.fillPath(ground, QColor("#6B8E23"))

        # Shed
        p.setBrush(QBrush(QColor("#8B6914")))
        p.setPen(Qt.NoPen)
        p.drawRect(w-180, int(h*0.25), 160, int(h*0.35))
        # Roof
        roof = QPolygon([
            QPoint(w-190, int(h*0.25)),
            QPoint(w-10, int(h*0.25)),
            QPoint(w-100, int(h*0.12)),
        ])
        p.setBrush(QBrush(QColor("#A0522D")))
        p.drawPolygon(roof)

        # Draw YOLO boxes
        if self._boxes:
            for box in self._boxes:
                bx = int(box["x"] / 100 * w)
                by = int(box["y"] / 100 * h * 0.8) + int(h*0.2)
                bw = int(box["w"] / 100 * w)
                bh = int(box["h"] / 100 * h * 0.8)

                color = QColor("#FF5722") if box["label"] == "疑似異常" else QColor("#4CAF50")
                pen = QPen(color, 2)
                p.setPen(pen)
                p.setBrush(Qt.NoBrush)
                p.drawRect(bx, by, bw, bh)

                # Corner accents
                cl = 8
                p.setPen(QPen(color, 3))
                p.drawLine(bx, by, bx+cl, by)
                p.drawLine(bx, by, bx, by+cl)
                p.drawLine(bx+bw-cl, by, bx+bw, by)
                p.drawLine(bx+bw, by, bx+bw, by+cl)
                p.drawLine(bx, by+bh-cl, bx, by+bh)
                p.drawLine(bx, by+bh, bx+cl, by+bh)
                p.drawLine(bx+bw-cl, by+bh, bx+bw, by+bh)
                p.drawLine(bx+bw, by+bh-cl, bx+bw, by+bh)

                # Label
                p.setPen(Qt.NoPen)
                label_bg = QColor(color)
                label_bg.setAlpha(200)
                p.setBrush(QBrush(label_bg))
                p.drawRoundedRect(bx, by-20, max(60, len(box["label"])*7+40), 18, 4, 4)
                p.setPen(Qt.white)
                p.setFont(QFont(Theme.FONT_BODY, 8))
                p.drawText(bx+4, by-5, f"{box['label']}  {box['conf']:.0%}")

        # HUD overlay
        p.setPen(Qt.NoPen)
        hud = QColor(0, 0, 0, 100)
        p.setBrush(QBrush(hud))
        p.drawRoundedRect(10, 10, 180, 56, 8, 8)
        p.setPen(QColor("#4CAF50"))
        p.setFont(QFont(Theme.FONT_MONO, 9))
        if self._data:
            p.drawText(18, 28, f"YOLO v8  ●  LIVE  {self._data['fps']} fps")
            p.drawText(18, 46, f"識別: {self._data['count']} 隻  |  avg conf: {self._data['conf_avg']:.0%}")
        else:
            p.drawText(18, 32, "YOLO v8  ●  等待中...")

        # Timestamp
        p.setPen(QColor("white"))
        p.setFont(QFont(Theme.FONT_MONO, 8))
        ts = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        p.drawText(w-160, h-12, ts)

        p.end()


class MonitorPage(QWidget):
    def __init__(self, yolo: YoloEngine, parent=None):
        super().__init__(parent)
        self.yolo = yolo

        self.model = None
        self.cap = None
        self.timer_camera = QTimer(self)
        self.timer_camera.timeout.connect(self._open_frame)
        self.is_camera_open = False
        self.output_size = 640
        self.current_source_mode = None

        self.results = None
        self.names = {}
        self.cls_list = []
        self.conf_list = []
        self.location_list = []
        self._last_frame = None

        self._init_detector()
        self._setup()
        yolo.detectionUpdated.connect(self._on_yolo)

    def _init_detector(self):
        if YOLO is None or np is None:
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base_dir, "runs", "detect", "train", "weights", "best.pt"),
            os.path.join(base_dir, "yolo11n.pt"),
            os.path.join(base_dir, "yolov8n.pt"),
        ]
        model_path = None
        for c in candidates:
            if os.path.exists(c):
                model_path = c
                break

        if not model_path:
            return

        try:
            self.model = YOLO(model_path, task="detect")
            self.model(np.zeros((48, 48, 3), dtype=np.uint8))
        except Exception:
            self.model = None

    def _setup(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(Theme.CONTENT_PAD, Theme.CONTENT_PAD,
                                Theme.CONTENT_PAD, Theme.CONTENT_PAD)
        root.setSpacing(16)

        # ── Control Bar ──────────────────────
        ctrl = self._control_bar()
        root.addWidget(ctrl)

        # ── Main Content ──────────────────────
        main = QHBoxLayout()
        main.setSpacing(16)

        # Left: Video canvas + bottom panels
        left_col = QVBoxLayout()
        left_col.setSpacing(12)

        self.canvas = YoloCanvas()
        canvas_frame = QFrame()
        canvas_frame.setStyleSheet(f"background:{Theme.BG_NAV}; border-radius:12px;")
        shadow(canvas_frame, 16, Theme.PRIMARY, 0.2)
        cf_lay = QVBoxLayout(canvas_frame)
        cf_lay.setContentsMargins(0, 0, 0, 0)
        cf_lay.addWidget(self.canvas)
        left_col.addWidget(canvas_frame)

        # Camera row
        cam_row = QHBoxLayout()
        cam_row.setSpacing(8)
        for i, label in enumerate(["圍欄A區","圍欄B區","圍欄C區","入口攝影機"]):
            cam_card = QFrame()
            cam_card.setFixedHeight(60)
            col = [Theme.PRIMARY, Theme.PRIMARY_DARK, Theme.ACCENT, Theme.WOOD_DARK][i]
            cam_card.setStyleSheet(f"background:{col}22; border:2px solid {col}55; border-radius:8px;")
            cam_card.setCursor(QCursor(Qt.PointingHandCursor))
            cam_lay = QVBoxLayout(cam_card)
            cam_lay.setAlignment(Qt.AlignCenter)
            cl = QLabel(f"📹 {label}")
            cl.setStyleSheet(f"font-size:11px; color:{Theme.TEXT_PRIMARY}; font-weight:600;")
            cl.setAlignment(Qt.AlignCenter)
            cam_lay.addWidget(cl)
            cam_row.addWidget(cam_card)
        left_col.addLayout(cam_row)
        main.addLayout(left_col, 3)

        # Right: data panels
        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        right_col.addWidget(self._yolo_data_panel())
        right_col.addWidget(self._env_panel())
        right_col.addWidget(self._alert_panel())
        main.addLayout(right_col, 1)

        root.addLayout(main)

    def _control_bar(self):
        bar = QFrame()
        bar.setFixedHeight(66)
        bar.setStyleSheet(f"background:white; border-radius:10px; border:1px solid {Theme.BORDER};")
        shadow(bar, 8, Theme.PRIMARY, 0.06)

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        self.btn_upload_image = GreenButton("🖼 圖片檢測", small=True, outlined=True)
        self.btn_upload_image.clicked.connect(self.upload_image)
        lay.addWidget(self.btn_upload_image)

        self.btn_upload_video = GreenButton("🎞 視頻回放", small=True, outlined=True)
        self.btn_upload_video.clicked.connect(self.open_video)
        lay.addWidget(self.btn_upload_video)

        self.btn_open_camera = GreenButton("📹 直播監控", small=True)
        self.btn_open_camera.clicked.connect(self.open_camera)
        lay.addWidget(self.btn_open_camera)

        self.btn_stop = GreenButton("⏹ 停止", small=True, outlined=True)
        self.btn_stop.clicked.connect(self.stop_video)
        lay.addWidget(self.btn_stop)

        lay.addWidget(self._vline())

        target_lbl = QLabel("目標：")
        target_lbl.setStyleSheet(f"font-size:13px; color:{Theme.TEXT_SECONDARY};")
        lay.addWidget(target_lbl)

        self.target_combo = QComboBox()
        self.target_combo.addItems(["全部"])
        self.target_combo.setFixedWidth(140)
        self.target_combo.currentIndexChanged.connect(self.on_target_change)
        self.target_combo.setStyleSheet(f"""
            QComboBox {{ border:1px solid {Theme.BORDER}; border-radius:6px;
                padding:4px 8px; font-size:12px; background:white; }}
        """)
        lay.addWidget(self.target_combo)

        lay.addStretch()

        # Quality
        q_label = QLabel("畫質：")
        q_label.setStyleSheet(f"font-size:13px; color:{Theme.TEXT_SECONDARY};")
        lay.addWidget(q_label)
        q_combo = QComboBox()
        q_combo.addItems(["1080p HD","720p","480p","自動"])
        q_combo.setStyleSheet(f"""
            QComboBox {{ border:1px solid {Theme.BORDER}; border-radius:6px;
                padding:4px 8px; font-size:12px; background:white; }}
        """)
        lay.addWidget(q_combo)

        lay.addWidget(self._vline())

        # Screenshot
        self.btn_screenshot = GreenButton("📸 截圖", small=True)
        self.btn_screenshot.clicked.connect(self.take_screenshot)
        lay.addWidget(self.btn_screenshot)

        # Full screen
        fs = GreenButton("⛶ 全螢幕", small=True, outlined=True)
        lay.addWidget(fs)

        return bar

    def _vline(self):
        v = QFrame()
        v.setFixedSize(1, 28)
        v.setStyleSheet(f"background:{Theme.BORDER};")
        return v

    def _yolo_data_panel(self):
        card = QFrame()
        card.setStyleSheet(f"background:white; border-radius:12px; border:1px solid {Theme.BORDER};")
        shadow(card, 12, Theme.PRIMARY, 0.08)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(8)

        h = QHBoxLayout()
        title = QLabel("🤖 YOLO 識別數據")
        title.setStyleSheet(f"font-size:14px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        h.addWidget(title)
        h.addStretch()
        yolo_dot = YoloIndicator()
        h.addWidget(yolo_dot)
        live = QLabel("即時")
        live.setStyleSheet(f"font-size:10px; color:{Theme.PRIMARY};")
        h.addWidget(live)
        lay.addLayout(h)

        self.yolo_rows = {}
        fields = [
            ("識別數量", "count", "—"),
            ("類別", "label", "—"),
            ("平均置信度", "conf_avg", "—"),
            ("當前置信度", "conf", "—"),
            ("幀率", "fps", "—"),
            ("xmin", "xmin", "—"),
            ("ymin", "ymin", "—"),
            ("xmax", "xmax", "—"),
            ("ymax", "ymax", "—"),
            ("當前時間", "timestamp", "—"),
            ("異常警報", "anomaly", "正常"),
        ]
        for label, key, default in fields:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_SECONDARY};")
            row.addWidget(lbl)
            row.addStretch()
            val = QLabel(default)
            val.setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.TEXT_PRIMARY};")
            row.addWidget(val)
            lay.addLayout(row)
            self.yolo_rows[key] = val

        return card

    def _env_panel(self):
        card = QFrame()
        card.setStyleSheet(f"background:white; border-radius:12px; border:1px solid {Theme.BORDER};")
        shadow(card, 12, Theme.PRIMARY, 0.08)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(8)

        title = QLabel("🌿 環境數據")
        title.setStyleSheet(f"font-size:14px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        env_data = [
            ("🌡️ 溫度", f"{MOCK_ENV['temp']}°C", 50, "#FF7043"),
            ("💧 濕度", f"{MOCK_ENV['humidity']}%", MOCK_ENV["humidity"], Theme.INFO),
            ("💨 CO₂", f"{MOCK_ENV['co2']}ppm", min(100,MOCK_ENV["co2"]//10), Theme.TEXT_SECONDARY),
            ("💡 光照", f"{MOCK_ENV['light']}lux", min(100,MOCK_ENV["light"]//10), Theme.GOLD),
            ("🌬️ 風速", f"{MOCK_ENV['wind']}m/s", int(MOCK_ENV["wind"]*20), Theme.PRIMARY),
        ]
        for label, val, prog, color in env_data:
            row = QVBoxLayout()
            row.setSpacing(2)
            h = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-size:11px; color:{Theme.TEXT_SECONDARY};")
            h.addWidget(lbl)
            h.addStretch()
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size:12px; font-weight:600; color:{color};")
            h.addWidget(vl)
            row.addLayout(h)
            bar = QProgressBar()
            bar.setRange(0,100); bar.setValue(prog)
            bar.setFixedHeight(5)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar {{ background:{Theme.BORDER}; border-radius:3px; }}
                QProgressBar::chunk {{ background:{color}; border-radius:3px; }}
            """)
            row.addWidget(bar)
            lay.addLayout(row)

        return card

    def _alert_panel(self):
        card = QFrame()
        card.setStyleSheet(f"background:{Theme.WARNING}15; border-radius:12px; border:1px solid {Theme.WARNING}44;")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(8)

        title = QLabel("⚠️ 異常提醒")
        title.setStyleSheet(f"font-size:14px; font-weight:700; color:{Theme.WARNING};")
        lay.addWidget(title)

        alerts = [
            "阿福 (C003)：活動頻率偏低",
            "B區：氨氣濃度偏高 12ppm",
        ]
        for a in alerts:
            al = QLabel(f"• {a}")
            al.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_PRIMARY};")
            al.setWordWrap(True)
            lay.addWidget(al)

        self.yolo_anomaly_label = QLabel("YOLO：目前無異常")
        self.yolo_anomaly_label.setStyleSheet(f"font-size:11px; color:{Theme.SUCCESS}; font-style:italic;")
        lay.addWidget(self.yolo_anomaly_label)

        return card

    def upload_image(self):
        if self.model is None:
            QMessageBox.warning(self, "YOLO", "未找到可用模型，請先確認 weights 文件。")
            return

        self.stop_video()
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose image", "", "Image files (*.jpg *.png *.jpeg *.bmp *.tif)")
        if not file_name:
            return

        self.current_source_mode = "image"
        t1 = time.time()
        results = self.model.predict(file_name, conf=0.25)[0]
        t2 = time.time()
        plotted = results.plot()
        self._last_frame = plotted
        self.canvas.update_frame(plotted)
        self._apply_results(results, t2 - t1, fps_text="—")

    def open_video(self):
        if self.model is None or cv2 is None:
            QMessageBox.warning(self, "YOLO", "未找到可用模型或 OpenCV 依賴。")
            return

        self.stop_video()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open video", "", "Video files (*.avi *.mp4 *.mov *.mkv)")
        if not file_path:
            return
        self.cap = cv2.VideoCapture(file_path)
        self.current_source_mode = "video"
        self.timer_camera.start(1)

    def open_camera(self):
        if self.model is None or cv2 is None:
            QMessageBox.warning(self, "YOLO", "未找到可用模型或 OpenCV 依賴。")
            return

        self.stop_video()
        self.cap = cv2.VideoCapture(0)
        if not self.cap or not self.cap.isOpened():
            QMessageBox.warning(self, "Camera", "無法打開攝像頭。")
            return
        self.is_camera_open = True
        self.current_source_mode = "camera"
        self.timer_camera.start(1)

    def stop_video(self):
        self.timer_camera.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_camera_open = False
        self.current_source_mode = None

    def _open_frame(self):
        if self.cap is None:
            return
        ret, frame = self.cap.read()
        if not ret:
            self.stop_video()
            return
        self._run_detection_on_frame(frame)

    def _run_detection_on_frame(self, frame):
        if self.model is None:
            return
        t1 = time.time()
        results = self.model.predict(frame, conf=0.25)[0]
        t2 = time.time()
        plotted = results.plot()
        elapsed = max(1e-6, t2 - t1)
        fps = f"{1.0 / elapsed:.1f} fps"
        self._last_frame = plotted
        self.canvas.update_frame(plotted)
        self._apply_results(results, elapsed, fps_text=fps)

    def _apply_results(self, results, elapsed_s, fps_text="—"):
        names = results.names
        location_list = results.boxes.xyxy.tolist()
        location_list = [list(map(int, e)) for e in location_list]
        cls_list = [int(i) for i in results.boxes.cls.tolist()]
        conf_list = ["%.2f %%" % (each * 100) for each in results.boxes.conf.tolist()]

        self.results = results
        self.names = names
        self.cls_list = cls_list
        self.conf_list = conf_list
        self.location_list = location_list

        choose_list = ["全部"] + [names[cid] + "_" + str(i) for i, cid in enumerate(cls_list)]
        self.target_combo.blockSignals(True)
        self.target_combo.clear()
        self.target_combo.addItems(choose_list)
        self.target_combo.blockSignals(False)

        self.yolo_rows["count"].setText(f"{len(location_list)} 隻")
        avg_conf = 0.0
        if len(results.boxes.conf) > 0:
            avg_conf = float(results.boxes.conf.mean().item())
        self.yolo_rows["conf_avg"].setText(f"{avg_conf:.0%}")
        self.yolo_rows["fps"].setText(fps_text)
        self.yolo_rows["timestamp"].setText(datetime.now().strftime("%H:%M:%S"))

        anomaly = any(names[cid] in ["疑似异常", "疑似異常", "abnormal"] for cid in cls_list)
        if anomaly:
            self.yolo_rows["anomaly"].setText("⚠️ 疑似異常")
            self.yolo_rows["anomaly"].setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.WARNING};")
            self.yolo_anomaly_label.setText("⚠️ YOLO 偵測到疑似異常！")
            self.yolo_anomaly_label.setStyleSheet(f"font-size:11px; color:{Theme.WARNING};")
        else:
            self.yolo_rows["anomaly"].setText("✓ 正常")
            self.yolo_rows["anomaly"].setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.SUCCESS};")
            self.yolo_anomaly_label.setText("YOLO：目前無異常")
            self.yolo_anomaly_label.setStyleSheet(f"font-size:11px; color:{Theme.SUCCESS};")

        if location_list:
            self._apply_target_detail(0)
        else:
            for key in ["label", "conf", "xmin", "ymin", "xmax", "ymax"]:
                self.yolo_rows[key].setText("—")

    def on_target_change(self, _index=None):
        if self.results is None:
            return
        text = self.target_combo.currentText()
        if text == "全部":
            idx = 0
            if self.location_list:
                self._apply_target_detail(idx)
            plotted = self.results.plot()
            self._last_frame = plotted
            self.canvas.update_frame(plotted)
            return

        try:
            idx = int(text.split("_")[-1])
            self._apply_target_detail(idx)
            plotted = self.results[idx].plot()
            self._last_frame = plotted
            self.canvas.update_frame(plotted)
        except Exception:
            pass

    def _apply_target_detail(self, index):
        if index >= len(self.location_list):
            return
        box = self.location_list[index]
        label = self.names[self.cls_list[index]] if index < len(self.cls_list) else "—"
        conf = self.conf_list[index] if index < len(self.conf_list) else "—"
        self.yolo_rows["label"].setText(label)
        self.yolo_rows["conf"].setText(conf)
        self.yolo_rows["xmin"].setText(str(box[0]))
        self.yolo_rows["ymin"].setText(str(box[1]))
        self.yolo_rows["xmax"].setText(str(box[2]))
        self.yolo_rows["ymax"].setText(str(box[3]))

    def take_screenshot(self):
        if self._last_frame is None or cv2 is None:
            QMessageBox.information(self, "截圖", "目前沒有可保存畫面。")
            return
        shot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "middle_file", "tmp")
        os.makedirs(shot_dir, exist_ok=True)
        file_path = os.path.join(shot_dir, f"monitor_shot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(file_path, self._last_frame)
        QMessageBox.information(self, "截圖", f"截圖已儲存\n{file_path}")

    def _on_yolo(self, data):
        if self.current_source_mode is not None:
            return
        self.canvas.update_detection(data)
        if "count" in self.yolo_rows:
            self.yolo_rows["count"].setText(f"{data['count']} 隻")
        if "conf_avg" in self.yolo_rows:
            self.yolo_rows["conf_avg"].setText(f"{data['conf_avg']:.0%}")
        if "fps" in self.yolo_rows:
            self.yolo_rows["fps"].setText(f"{data['fps']} fps")
        if "label" in self.yolo_rows and data.get("boxes"):
            self.yolo_rows["label"].setText(data["boxes"][0].get("label", "—"))
        if "conf" in self.yolo_rows and data.get("boxes"):
            self.yolo_rows["conf"].setText(f"{data['boxes'][0].get('conf', 0):.2%}")
        if "xmin" in self.yolo_rows and data.get("boxes"):
            self.yolo_rows["xmin"].setText(str(data["boxes"][0].get("x", "—")))
        if "ymin" in self.yolo_rows and data.get("boxes"):
            self.yolo_rows["ymin"].setText(str(data["boxes"][0].get("y", "—")))
        if "xmax" in self.yolo_rows and data.get("boxes"):
            self.yolo_rows["xmax"].setText(str(data["boxes"][0].get("w", "—")))
        if "ymax" in self.yolo_rows and data.get("boxes"):
            self.yolo_rows["ymax"].setText(str(data["boxes"][0].get("h", "—")))
        if "timestamp" in self.yolo_rows:
            self.yolo_rows["timestamp"].setText(data["timestamp"])
        if "anomaly" in self.yolo_rows:
            if data["anomaly"]:
                self.yolo_rows["anomaly"].setText("⚠️ 疑似異常")
                self.yolo_rows["anomaly"].setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.WARNING};")
                self.yolo_anomaly_label.setText("⚠️ YOLO 偵測到疑似異常！")
                self.yolo_anomaly_label.setStyleSheet(f"font-size:11px; color:{Theme.WARNING};")
            else:
                self.yolo_rows["anomaly"].setText("✓ 正常")
                self.yolo_rows["anomaly"].setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.SUCCESS};")
                self.yolo_anomaly_label.setText("YOLO：目前無異常")
                self.yolo_anomaly_label.setStyleSheet(f"font-size:11px; color:{Theme.SUCCESS};")

    def closeEvent(self, e):
        self.stop_video()
        super().closeEvent(e)


# ─────────────────────────────────────────────
#  PAGE 3: MY ADOPTION
# ─────────────────────────────────────────────
class AdoptionPage(QWidget):
    navigate = Signal(int)

    def __init__(self, yolo: YoloEngine, parent=None):
        super().__init__(parent)
        self.yolo = yolo
        self._selected = 0
        self._setup()
        yolo.detectionUpdated.connect(self._on_yolo)

    def _setup(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(Theme.CONTENT_PAD, Theme.CONTENT_PAD,
                                Theme.CONTENT_PAD, Theme.CONTENT_PAD)
        root.setSpacing(16)

        # Left: chicken list
        left = QVBoxLayout()
        left.setSpacing(12)

        header = QHBoxLayout()
        t = SectionTitle("我的認養")
        header.addWidget(t)
        header.addStretch()
        add_btn = GreenButton("+ 新增認養", small=True)
        header.addWidget(add_btn)
        left.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_w = QWidget()
        scroll_w.setStyleSheet("background:transparent;")
        scroll_lay = QVBoxLayout(scroll_w)
        scroll_lay.setSpacing(10)
        scroll_lay.setContentsMargins(0, 0, 0, 0)

        self._chicken_cards = []
        for i, c in enumerate(MOCK_CHICKENS):
            card = self._chicken_list_item(i, c)
            scroll_lay.addWidget(card)
            self._chicken_cards.append(card)

        scroll_lay.addStretch()
        scroll.setWidget(scroll_w)
        left.addWidget(scroll)

        root.addLayout(left, 2)

        # Right: detail + feed + log
        self.detail_stack = QStackedWidget()
        for i, c in enumerate(MOCK_CHICKENS):
            detail = self._chicken_detail(c)
            self.detail_stack.addWidget(detail)

        root.addWidget(self.detail_stack, 3)

    def _chicken_list_item(self, idx, c):
        card = HoverCard(hover_bg=Theme.PRIMARY_PALE)
        card.setFixedHeight(80)
        card.clicked.connect(lambda i=idx: self._select(i))
        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        av = ChickenAvatar(c["img_color"], 48)
        lay.addWidget(av)

        info = QVBoxLayout()
        info.setSpacing(3)
        name_row = QHBoxLayout()
        name = QLabel(c["name"])
        name.setStyleSheet(f"font-size:15px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        name_row.addWidget(name)
        status_color = Theme.SUCCESS if c["status"] == "健康" else Theme.WARNING
        b = Badge(c["status"], status_color)
        name_row.addWidget(b)
        name_row.addStretch()
        info.addLayout(name_row)

        sub = QLabel(f"{c['breed']}  ·  {c['location']}")
        sub.setStyleSheet(f"font-size:11px; color:{Theme.TEXT_SECONDARY};")
        info.addWidget(sub)

        lay.addLayout(info)

        health = QLabel(f"♥ {c['health']}%")
        health.setStyleSheet(f"font-size:13px; font-weight:600; color:{status_color};")
        lay.addWidget(health)

        return card

    def _chicken_detail(self, c):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w)
        lay.setSpacing(14)
        lay.setContentsMargins(0, 0, 0, 0)

        # Header card
        header = HoverCard()
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 20, 24, 20)
        h_lay.setSpacing(20)

        av = ChickenAvatar(c["img_color"], 80)
        h_lay.addWidget(av)

        info = QVBoxLayout()
        info.setSpacing(6)
        name_row = QHBoxLayout()
        name = QLabel(c["name"])
        name.setStyleSheet(f"font-size:22px; font-weight:700; color:{Theme.TEXT_PRIMARY}; font-family:Georgia;")
        name_row.addWidget(name)
        name_row.addSpacing(8)
        status_c = Theme.SUCCESS if c["status"] == "健康" else Theme.WARNING
        b = Badge(c["status"], status_c)
        name_row.addWidget(b)
        name_row.addStretch()

        edit = GreenButton("✏️ 改名", small=True, outlined=True)
        edit.clicked.connect(lambda ch=c: self._rename(ch))
        name_row.addWidget(edit)
        info.addLayout(name_row)

        meta = QLabel(f"品種：{c['breed']}  ·  雞齡：{c['age']} 天  ·  位置：{c['location']}")
        meta.setStyleSheet(f"font-size:13px; color:{Theme.TEXT_SECONDARY};")
        info.addWidget(meta)

        stats = QHBoxLayout()
        stats.setSpacing(24)
        for label, val, color in [
            ("體重", f"{c['weight']}kg", Theme.PRIMARY),
            ("健康", f"{c['health']}%", status_c),
            ("產蛋", f"{c['eggs_total']}枚", Theme.GOLD),
        ]:
            sv = QVBoxLayout()
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size:20px; font-weight:700; color:{color};")
            sv.addWidget(vl)
            sl = QLabel(label)
            sl.setStyleSheet(f"font-size:11px; color:{Theme.TEXT_MUTED};")
            sv.addWidget(sl)
            stats.addLayout(sv)
        stats.addStretch()

        monitor_btn = GreenButton("📹 跳轉監控定位", small=True)
        monitor_btn.clicked.connect(lambda: self.navigate.emit(1))
        stats.addWidget(monitor_btn)

        info.addLayout(stats)
        h_lay.addLayout(info)
        lay.addWidget(header)

        # Tabs: feed / logs
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border:1px solid {Theme.BORDER}; border-radius:10px; background:white; }}
            QTabBar::tab {{ padding:8px 20px; font-size:13px; color:{Theme.TEXT_SECONDARY}; border:none; }}
            QTabBar::tab:selected {{ color:{Theme.PRIMARY}; font-weight:700;
                border-bottom:3px solid {Theme.PRIMARY}; }}
        """)
        tabs.addTab(self._feed_tab(c), "🌾 飼料定制")
        tabs.addTab(self._log_tab(c), "📋 生長日誌")
        tabs.addTab(self._yolo_tab(c), "🤖 YOLO 數據")
        lay.addWidget(tabs)

        return w

    def _feed_tab(self, c):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        lay.addWidget(QLabel("當前配方："))

        recipes = [
            ("有機玉米", 40, Theme.GOLD),
            ("豆粕蛋白", 25, Theme.PRIMARY),
            ("麥麩", 15, Theme.WOOD_DARK),
            ("鈣質補充", 10, Theme.INFO),
            ("益生菌", 10, Theme.ACCENT),
        ]
        for name, pct, color in recipes:
            row = QHBoxLayout()
            lbl = QLabel(name)
            lbl.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_PRIMARY}; min-width:80px;")
            row.addWidget(lbl)
            bar = QProgressBar()
            bar.setRange(0,100); bar.setValue(pct)
            bar.setFixedHeight(10)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar {{ background:{Theme.BORDER}; border-radius:5px; }}
                QProgressBar::chunk {{ background:{color}; border-radius:5px; }}
            """)
            row.addWidget(bar)
            pl = QLabel(f"{pct}%")
            pl.setStyleSheet(f"font-size:12px; color:{color}; min-width:35px;")
            row.addWidget(pl)
            lay.addLayout(row)

        lay.addSpacing(8)
        price_row = QHBoxLayout()
        price_row.addWidget(QLabel("月度費用："))
        price_lbl = QLabel("HK$85/月")
        price_lbl.setStyleSheet(f"font-size:18px; font-weight:700; color:{Theme.PRIMARY};")
        price_row.addWidget(price_lbl)
        price_row.addStretch()
        custom_btn = GreenButton("定制配方", small=True)
        price_row.addWidget(custom_btn)
        lay.addLayout(price_row)
        lay.addStretch()
        return w

    def _log_tab(self, c):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(0)

        for log in MOCK_LOGS:
            if log["chicken"] == c["id"] or True:
                row = QFrame()
                row.setFixedHeight(48)
                row.setStyleSheet(f"border-bottom:1px solid {Theme.BORDER};")
                rl = QHBoxLayout(row)
                rl.setContentsMargins(0, 0, 0, 0)
                rl.setSpacing(12)

                ico = {"ai":"🤖","egg":"🥚","feed":"🌾","health":"💊"}.get(log["type"],"📌")
                il = QLabel(ico)
                il.setFixedWidth(24)
                rl.addWidget(il)

                date = QLabel(log["date"])
                date.setStyleSheet(f"font-size:11px; color:{Theme.TEXT_MUTED}; min-width:130px;")
                rl.addWidget(date)

                event = QLabel(log["event"])
                event.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_PRIMARY};")
                rl.addWidget(event)
                rl.addStretch()
                lay.addWidget(row)

        lay.addStretch()
        return w

    def _yolo_tab(self, c):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(10)

        info = QLabel("此頁面同步 YOLO 即時識別數據")
        info.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_MUTED}; font-style:italic;")
        lay.addWidget(info)

        self.yolo_detail_rows = {}
        fields = [("體重估算","—"),("活動指數","—"),("羽毛狀態","—"),("上次識別","—")]
        for label, default in fields:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet(f"font-size:13px; color:{Theme.TEXT_SECONDARY}; min-width:100px;")
            row.addWidget(lbl)
            val = QLabel(default)
            val.setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.TEXT_PRIMARY};")
            row.addWidget(val)
            row.addStretch()
            lay.addLayout(row)
            self.yolo_detail_rows[label] = val

        lay.addStretch()
        return w

    def _select(self, idx):
        self._selected = idx
        self.detail_stack.setCurrentIndex(idx)

    def _rename(self, c):
        name, ok = QInputDialog_simple(self, f"為 {c['name']} 改名", "新名稱：")
        if ok and name:
            QMessageBox.information(self, "改名成功", f"已將 {c['name']} 改名為：{name} ✓")

    def _on_yolo(self, data):
        if hasattr(self, 'yolo_detail_rows'):
            w = round(MOCK_CHICKENS[self._selected]["weight"] + random.uniform(-0.1, 0.1), 2)
            self.yolo_detail_rows["體重估算"].setText(f"{w} kg")
            act = random.randint(60, 100)
            self.yolo_detail_rows["活動指數"].setText(f"{act}%")
            self.yolo_detail_rows["羽毛狀態"].setText(random.choice(["光澤良好","略顯暗淡","正常"]))
            self.yolo_detail_rows["上次識別"].setText(data["timestamp"])


def QInputDialog_simple(parent, title, label):
    """Simple input dialog wrapper"""
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setFixedSize(320, 140)
    dialog.setStyleSheet(f"background:{Theme.BG}; font-family:'{Theme.FONT_BODY}';")
    lay = QVBoxLayout(dialog)
    lay.setSpacing(12)
    lbl = QLabel(label)
    lay.addWidget(lbl)
    edit = QLineEdit()
    edit.setStyleSheet(f"border:1.5px solid {Theme.BORDER}; border-radius:6px; padding:6px 10px; font-size:13px;")
    lay.addWidget(edit)
    btns = QHBoxLayout()
    ok = GreenButton("確認", small=True)
    cancel = GreenButton("取消", small=True, outlined=True)
    btns.addWidget(ok)
    btns.addWidget(cancel)
    lay.addLayout(btns)
    result = [None, False]
    ok.clicked.connect(lambda: [result.__setitem__(0, edit.text()), result.__setitem__(1, True), dialog.accept()])
    cancel.clicked.connect(dialog.reject)
    dialog.exec()
    return result[0], result[1]


# ─────────────────────────────────────────────
#  PAGE 4: SUBSCRIPTION ORDERS
# ─────────────────────────────────────────────
class OrdersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup()

    def _setup(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(Theme.CONTENT_PAD, Theme.CONTENT_PAD,
                                Theme.CONTENT_PAD, Theme.CONTENT_PAD)
        root.setSpacing(20)

        # Header
        hdr = QHBoxLayout()
        hdr.addWidget(SectionTitle("訂閱訂單"))
        hdr.addStretch()
        add = GreenButton("+ 新增訂閱", small=True)
        hdr.addWidget(add)
        root.addLayout(hdr)

        # Main content
        content = QHBoxLayout()
        content.setSpacing(16)

        # Left: order list
        left = QVBoxLayout()
        left.setSpacing(12)

        for o in MOCK_ORDERS:
            left.addWidget(self._order_card(o))
        left.addStretch()

        content.addLayout(left, 3)

        # Right: delivery settings
        right = QVBoxLayout()
        right.setSpacing(12)
        right.addWidget(self._delivery_panel())
        right.addWidget(self._payment_panel())
        right.addStretch()

        content.addLayout(right, 2)
        root.addLayout(content)

    def _order_card(self, o):
        card = HoverCard()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)

        # Top row
        top = QHBoxLayout()
        plan = QLabel(o["plan"])
        plan.setStyleSheet(f"font-size:16px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        top.addWidget(plan)
        top.addStretch()
        status_colors = {"配送中": Theme.INFO, "待配送": Theme.WARNING, "已完成": Theme.TEXT_MUTED}
        b = Badge(o["status"], status_colors.get(o["status"], Theme.SUCCESS))
        top.addWidget(b)
        lay.addLayout(top)

        # Meta
        meta = QHBoxLayout()
        meta.setSpacing(20)
        for label, val in [("訂單號", o["id"]),("數量", o["qty"]),("費用", o["price"]),("下單日期", o["date"])]:
            mv = QVBoxLayout()
            mv.setSpacing(2)
            ml = QLabel(label)
            ml.setStyleSheet(f"font-size:10px; color:{Theme.TEXT_MUTED};")
            mv.addWidget(ml)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.TEXT_PRIMARY};")
            mv.addWidget(vl)
            meta.addLayout(mv)
        meta.addStretch()
        lay.addLayout(meta)

        # Bottom row
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        addr = QLabel(f"📍 {o['address']}")
        addr.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_SECONDARY};")
        bottom.addWidget(addr)
        bottom.addStretch()

        if o["status"] != "已完成":
            modify = GreenButton("修改", small=True, outlined=True)
            pause = QPushButton("暫停")
            pause.setStyleSheet(f"""
                QPushButton {{ background:transparent; color:{Theme.WARNING};
                    border:1px solid {Theme.WARNING}; border-radius:6px;
                    padding:4px 12px; font-size:12px; }}
                QPushButton:hover {{ background:{Theme.WARNING}18; }}
            """)
            pause.setCursor(QCursor(Qt.PointingHandCursor))
            bottom.addWidget(modify)
            bottom.addWidget(pause)

        trace = GreenButton("溯源憑證", small=True)
        trace.clicked.connect(lambda t=o["trace"]: self._show_trace(t))
        bottom.addWidget(trace)

        invoice = GreenButton("電子發票", small=True, outlined=True)
        invoice.clicked.connect(lambda: QMessageBox.information(self, "發票", "電子發票已生成，正在下載… ✓"))
        bottom.addWidget(invoice)

        lay.addLayout(bottom)
        return card

    def _show_trace(self, trace_id):
        dlg = QDialog(self)
        dlg.setWindowTitle("溯源憑證")
        dlg.setFixedSize(460, 360)
        dlg.setStyleSheet(f"background:{Theme.BG}; font-family:'{Theme.FONT_BODY}';")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        title = QLabel(f"🏷️ 溯源憑證  {trace_id}")
        title.setStyleSheet(f"font-size:18px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        for label, val in [
            ("農場名稱", "大嶼山生態農場"),
            ("養殖批次", trace_id),
            ("出欄日期", "2025-07-15"),
            ("認證機構", "香港有機農業協會"),
            ("YOLO截圖記錄", "共 127 張（點擊查看）"),
            ("飼養天數", "112 天"),
            ("飼料來源", "廣東有機農場 · 批次#2025-06"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label + "：")
            lbl.setStyleSheet(f"font-size:13px; color:{Theme.TEXT_MUTED}; min-width:120px;")
            row.addWidget(lbl)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size:13px; font-weight:600; color:{Theme.TEXT_PRIMARY};")
            row.addWidget(vl)
            row.addStretch()
            lay.addLayout(row)

        close = GreenButton("關閉", small=True)
        close.clicked.connect(dlg.accept)
        lay.addWidget(close, 0, Qt.AlignRight)
        dlg.exec()

    def _delivery_panel(self):
        card = HoverCard()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)

        title = QLabel("🚚 配送設置")
        title.setStyleSheet(f"font-size:14px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        for label, val in [("配送地址", "九龍塘德雅道15號"),("配送時段","10:00-13:00（週三/週六）"),("聯絡人","陳大文先生"),("聯絡電話","9XXX-XXXX")]:
            row = QHBoxLayout()
            lbl = QLabel(label + "：")
            lbl.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_MUTED}; min-width:70px;")
            row.addWidget(lbl)
            vl = QLabel(val)
            vl.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_PRIMARY};")
            row.addWidget(vl)
            row.addStretch()
            lay.addLayout(row)

        edit = GreenButton("修改配送設置", small=True, outlined=True)
        lay.addWidget(edit)
        return card

    def _payment_panel(self):
        card = HoverCard()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)

        title = QLabel("💳 付款方式")
        title.setStyleSheet(f"font-size:14px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        methods = [("八達通", "●", "#1B5E20", True), ("支付寶HK", "●", "#1677FF", False), ("信用卡", "●", "#B71C1C", False)]
        for name, ico, color, active in methods:
            row = QHBoxLayout()
            dot = QLabel(ico)
            dot.setStyleSheet(f"color:{color}; font-size:14px;")
            row.addWidget(dot)
            lbl = QLabel(name)
            lbl.setStyleSheet(f"font-size:13px; {'font-weight:700; color:'+Theme.TEXT_PRIMARY if active else 'color:'+Theme.TEXT_MUTED};")
            row.addWidget(lbl)
            row.addStretch()
            if active:
                b = Badge("使用中", Theme.SUCCESS)
                row.addWidget(b)
            lay.addLayout(row)

        change = GreenButton("更改付款方式", small=True, outlined=True)
        lay.addWidget(change)
        return card


# ─────────────────────────────────────────────
#  PAGE 5: PERSONAL CENTER
# ─────────────────────────────────────────────
class ProfilePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup()

    def _setup(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(Theme.CONTENT_PAD, Theme.CONTENT_PAD,
                                Theme.CONTENT_PAD, Theme.CONTENT_PAD)
        root.setSpacing(16)

        # Left: profile card + quick links
        left = QVBoxLayout()
        left.setSpacing(14)
        left.addWidget(self._profile_card())
        left.addWidget(self._quick_links())
        left.addStretch()

        root.addLayout(left, 1)

        # Right: tabs
        right = QVBoxLayout()
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border:1px solid {Theme.BORDER}; border-radius:12px; background:white; }}
            QTabBar::tab {{ padding:10px 22px; font-size:13px; color:{Theme.TEXT_SECONDARY}; border:none; }}
            QTabBar::tab:selected {{ color:{Theme.PRIMARY}; font-weight:700;
                border-bottom:3px solid {Theme.PRIMARY}; }}
        """)
        tabs.addTab(self._membership_tab(), "👑 會員")
        tabs.addTab(self._help_tab(), "❓ 幫助中心")
        tabs.addTab(self._feedback_tab(), "💬 意見反饋")
        tabs.addTab(self._settings_tab(), "⚙️ 設置")
        right.addWidget(tabs)

        root.addLayout(right, 2)

    def _profile_card(self):
        card = HoverCard()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(12)
        lay.setAlignment(Qt.AlignCenter)

        # Avatar
        av = QLabel("陳")
        av.setFixedSize(80, 80)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {Theme.PRIMARY_LIGHT}, stop:1 {Theme.PRIMARY_DARK});
            color:white; border-radius:40px;
            font-size:30px; font-weight:700;
        """)
        lay.addWidget(av, 0, Qt.AlignCenter)

        name = QLabel("陳大文")
        name.setStyleSheet(f"font-size:18px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        name.setAlignment(Qt.AlignCenter)
        lay.addWidget(name)

        member = QLabel("👑 黃金會員  ·  加入 312 天")
        member.setStyleSheet(f"font-size:12px; color:{Theme.GOLD}; font-weight:600;")
        member.setAlignment(Qt.AlignCenter)
        lay.addWidget(member)

        farm = QLabel("大嶼山生態農場")
        farm.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_SECONDARY};")
        farm.setAlignment(Qt.AlignCenter)
        lay.addWidget(farm)

        edit = GreenButton("編輯資料", small=True, outlined=True)
        lay.addWidget(edit, 0, Qt.AlignCenter)

        return card

    def _quick_links(self):
        card = HoverCard()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(4)

        title = QLabel("快速入口")
        title.setStyleSheet(f"font-size:14px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        links = [
            ("📹", "監控報告下載"),
            ("🐔", "認養服務條款"),
            ("📦", "配送查詢"),
            ("🔔", "通知設置"),
            ("🔒", "帳號安全"),
            ("📱", "手機版下載"),
        ]
        for ico, lbl in links:
            btn = QPushButton(f"  {ico}  {lbl}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:transparent;
                    color:{Theme.TEXT_PRIMARY};
                    border:none; border-radius:6px;
                    padding:8px 12px; font-size:13px;
                    text-align:left;
                }}
                QPushButton:hover {{
                    background:{Theme.PRIMARY_PALE};
                    color:{Theme.PRIMARY};
                }}
            """)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            lay.addWidget(btn)

        return card

    def _membership_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)

        # Current plan
        plan_frame = QFrame()
        plan_frame.setStyleSheet(f"""
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {Theme.GOLD}, stop:1 #FF8F00);
            border-radius:12px;
        """)
        plan_lay = QHBoxLayout(plan_frame)
        plan_lay.setContentsMargins(24, 20, 24, 20)
        plan_lay.setSpacing(16)

        pl = QVBoxLayout()
        pt = QLabel("👑 黃金會員")
        pt.setStyleSheet("font-size:22px; font-weight:700; color:white;")
        pl.addWidget(pt)
        ps = QLabel("有效期至：2026年1月15日  ·  剩餘 214 天")
        ps.setStyleSheet("font-size:13px; color:rgba(255,255,255,0.85);")
        pl.addWidget(ps)
        plan_lay.addLayout(pl)
        plan_lay.addStretch()

        renew = QPushButton("立即續費")
        renew.setStyleSheet("""
            QPushButton { background:white; color:#F9A825; border:none;
                border-radius:8px; padding:10px 20px; font-size:14px; font-weight:700; }
            QPushButton:hover { background:#FFF8E1; }
        """)
        renew.setCursor(QCursor(Qt.PointingHandCursor))
        renew.clicked.connect(lambda: self._renew_dialog())
        plan_lay.addWidget(renew)
        lay.addWidget(plan_frame)

        # Benefits
        benefits_title = QLabel("會員權益")
        benefits_title.setStyleSheet(f"font-size:16px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(benefits_title)

        benefits = [
            ("✓", "無限次農場實時監控訪問", True),
            ("✓", "YOLO AI識別數據完整版", True),
            ("✓", "優先配送（週三/週六）", True),
            ("✓", "專屬客服熱線", True),
            ("✓", "季度農場探訪（1次/季）", True),
        ]
        for ico, text, active in benefits:
            row = QHBoxLayout()
            il = QLabel(ico)
            il.setStyleSheet(f"color:{Theme.SUCCESS}; font-size:14px; font-weight:700; min-width:20px;")
            row.addWidget(il)
            tl = QLabel(text)
            tl.setStyleSheet(f"font-size:13px; color:{Theme.TEXT_PRIMARY if active else Theme.TEXT_MUTED};")
            row.addWidget(tl)
            row.addStretch()
            lay.addLayout(row)

        lay.addStretch()
        return w

    def _help_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(12)

        search = QLineEdit()
        search.setPlaceholderText("🔍  搜索常見問題…")
        search.setStyleSheet(f"""
            QLineEdit {{ border:1.5px solid {Theme.BORDER}; border-radius:8px;
                padding:10px 14px; font-size:13px; }}
            QLineEdit:focus {{ border-color:{Theme.PRIMARY}; }}
        """)
        lay.addWidget(search)

        faqs = [
            ("監控/識別", [
                ("YOLO識別精度如何？", "本系統採用 YOLOv8 模型，在農場場景下識別精度達 94.7%，可識別鸡只位置、行為狀態及異常情況。"),
                ("為何部分鸡只沒有被框選？", "可能是因為鸡只被遮擋或光線不足。建議在白天光線充足時段查看，或調整攝影機角度。"),
                ("如何下載監控截圖？", "在監控頁面點擊「截圖」或使用 Ctrl+S 快捷鍵，截圖自動儲存至本地，保存 7 天。"),
            ]),
            ("認養服務", [
                ("如何認養更多鸡只？", "在「我的認養」頁點擊「新增認養」，選擇品種後完成支付即可。每個帳號最多認養 10 隻。"),
                ("認養費用包含哪些服務？", "包含：飼料費、日常飼養管理、YOLO健康監測、月度健康報告及配送服務。"),
            ]),
        ]

        for category, items in faqs:
            cat_lbl = QLabel(f"📂  {category}")
            cat_lbl.setStyleSheet(f"font-size:13px; font-weight:700; color:{Theme.PRIMARY}; margin-top:8px;")
            lay.addWidget(cat_lbl)

            for q, a in items:
                q_btn = QPushButton(f"  Q: {q}")
                q_btn.setStyleSheet(f"""
                    QPushButton {{
                        background:{Theme.BG};
                        color:{Theme.TEXT_PRIMARY};
                        border:1px solid {Theme.BORDER};
                        border-radius:8px;
                        padding:10px 14px;
                        font-size:12px;
                        text-align:left;
                    }}
                    QPushButton:hover {{ background:{Theme.PRIMARY_PALE}; border-color:{Theme.PRIMARY}; }}
                """)
                q_btn.setCursor(QCursor(Qt.PointingHandCursor))
                q_btn.clicked.connect(lambda _, _a=a, _q=q: QMessageBox.information(w, _q, _a))
                lay.addWidget(q_btn)

        lay.addStretch()
        contact = GreenButton("📞 聯繫在線客服", outlined=True)
        lay.addWidget(contact)
        return w

    def _feedback_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("反饋類型："))
        combo = QComboBox()
        combo.addItems(["功能建議","問題反饋","監控/識別問題","其他"])
        combo.setStyleSheet(f"""
            QComboBox {{ border:1.5px solid {Theme.BORDER}; border-radius:8px;
                padding:8px 12px; font-size:13px; min-width:180px; }}
            QComboBox:focus {{ border-color:{Theme.PRIMARY}; }}
        """)
        type_row.addWidget(combo)
        type_row.addStretch()
        lay.addLayout(type_row)

        lay.addWidget(QLabel("詳細描述："))
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("請描述您遇到的問題或建議…")
        text_edit.setFixedHeight(100)
        text_edit.setStyleSheet(f"""
            QTextEdit {{ border:1.5px solid {Theme.BORDER}; border-radius:8px;
                padding:10px; font-size:13px; }}
            QTextEdit:focus {{ border-color:{Theme.PRIMARY}; }}
        """)
        lay.addWidget(text_edit)

        # Upload screenshot
        upload_frame = QFrame()
        upload_frame.setFixedHeight(80)
        upload_frame.setStyleSheet(f"""
            border:2px dashed {Theme.BORDER};
            border-radius:10px; background:{Theme.BG};
        """)
        upload_frame.setCursor(QCursor(Qt.PointingHandCursor))
        ul = QVBoxLayout(upload_frame)
        ul.setAlignment(Qt.AlignCenter)
        ul_lbl = QLabel("📎  點擊上傳截圖（支持 YOLO 監控異常截圖）")
        ul_lbl.setStyleSheet(f"font-size:12px; color:{Theme.TEXT_MUTED};")
        ul_lbl.setAlignment(Qt.AlignCenter)
        ul.addWidget(ul_lbl)
        lay.addWidget(upload_frame)
        upload_frame.mousePressEvent = lambda e: QFileDialog.getOpenFileName(w, "選擇截圖", "", "圖片 (*.png *.jpg *.jpeg)")

        submit = GreenButton("提交反饋")
        submit.clicked.connect(lambda: QMessageBox.information(w, "提交成功", "感謝您的反饋！我們將在 24 小時內回覆。✓"))
        lay.addWidget(submit)
        lay.addStretch()
        return w

    def _settings_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        sections = [
            ("通知設置", [
                ("YOLO 異常提醒（推送）", True),
                ("產蛋記錄通知", True),
                ("配送狀態更新", True),
                ("農場環境預警", True),
            ]),
            ("顯示設置", [
                ("啟動時自動播放監控", False),
                ("深色模式（Beta）", False),
                ("識別框顯示置信度", True),
            ]),
        ]

        for sec_title, items in sections:
            tl = QLabel(sec_title)
            tl.setStyleSheet(f"font-size:14px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
            lay.addWidget(tl)

            for label, checked in items:
                row = QHBoxLayout()
                lbl = QLabel(label)
                lbl.setStyleSheet(f"font-size:13px; color:{Theme.TEXT_PRIMARY};")
                row.addWidget(lbl)
                row.addStretch()
                cb = QCheckBox()
                cb.setChecked(checked)
                cb.setStyleSheet(f"""
                    QCheckBox::indicator {{ width:20px; height:20px; border-radius:4px;
                        border:2px solid {Theme.BORDER}; }}
                    QCheckBox::indicator:checked {{
                        background:{Theme.PRIMARY}; border-color:{Theme.PRIMARY};
                    }}
                """)
                row.addWidget(cb)
                lay.addLayout(row)

            lay.addSpacing(8)

        lay.addStretch()
        save = GreenButton("儲存設置")
        save.clicked.connect(lambda: QMessageBox.information(w, "設置", "設置已儲存 ✓"))
        lay.addWidget(save, 0, Qt.AlignRight)
        return w

    def _renew_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("會員續費")
        dlg.setFixedSize(400, 320)
        dlg.setStyleSheet(f"background:{Theme.BG}; font-family:'{Theme.FONT_BODY}';")
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        title = QLabel("選擇續費方案")
        title.setStyleSheet(f"font-size:18px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
        lay.addWidget(title)

        plans = [("3個月", "HK$480", "原價HK$560"), ("6個月", "HK$880", "原價HK$1120"), ("12個月", "HK$1580", "原價HK$2240")]
        for duration, price, original in plans:
            p_card = QFrame()
            p_card.setStyleSheet(f"background:white; border:1.5px solid {Theme.BORDER}; border-radius:10px;")
            p_card.setCursor(QCursor(Qt.PointingHandCursor))
            pl = QHBoxLayout(p_card)
            pl.setContentsMargins(16, 12, 16, 12)
            dl = QLabel(duration)
            dl.setStyleSheet(f"font-size:14px; font-weight:700; color:{Theme.TEXT_PRIMARY};")
            pl.addWidget(dl)
            pl.addStretch()
            orig = QLabel(original)
            orig.setStyleSheet(f"font-size:11px; color:{Theme.TEXT_MUTED}; text-decoration:line-through;")
            pl.addWidget(orig)
            pl.addSpacing(8)
            pr = QLabel(price)
            pr.setStyleSheet(f"font-size:16px; font-weight:700; color:{Theme.PRIMARY};")
            pl.addWidget(pr)
            lay.addWidget(p_card)

        btns = QHBoxLayout()
        ok = GreenButton("確認支付（八達通）")
        ok.clicked.connect(lambda: [dlg.accept(), QMessageBox.information(self, "支付成功", "會員已續費成功 ✓")])
        cancel = GreenButton("取消", outlined=True, small=True)
        cancel.clicked.connect(dlg.reject)
        btns.addWidget(ok)
        btns.addWidget(cancel)
        lay.addLayout(btns)
        dlg.exec()


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
class MetaFarmApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meta Farm  —  智慧農場管理平台")
        self.setMinimumSize(1200, 768)
        self.resize(1400, 860)

        # YOLO engine
        self.yolo = YoloEngine()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(f"background:{Theme.BG};")

        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # Sidebar
        self.nav = SideNav()
        self.nav.pageChanged.connect(self._navigate)
        main_lay.addWidget(self.nav)

        # Right column
        right = QWidget()
        right.setStyleSheet(f"background:{Theme.BG};")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        # Top bar
        self.topbar = TopBar()
        right_lay.addWidget(self.topbar)

        # Page stack (scrollable)
        self.stack = QStackedWidget()
        right_lay.addWidget(self.stack)

        main_lay.addWidget(right)

        # Build pages
        self._pages = []
        page_names = ["農場首頁", "農場監控", "我的認養", "訂閱訂單", "個人中心"]

        dashboard = DashboardPage(self.yolo)
        dashboard.navigate.connect(self._navigate)

        monitor = MonitorPage(self.yolo)

        adoption = AdoptionPage(self.yolo)
        adoption.navigate.connect(self._navigate)

        orders = OrdersPage()
        profile = ProfilePage()

        for page in [dashboard, monitor, adoption, orders, profile]:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setStyleSheet(f"background:{Theme.BG}; border:none;")
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setWidget(page)
            self.stack.addWidget(scroll)

        self._page_names = page_names

        # Shortcuts
        QShortcut(QKeySequence("F1"), self).activated.connect(lambda: self._navigate(4))
        QShortcut(QKeySequence("F5"), self).activated.connect(self._refresh)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(
            lambda: QMessageBox.information(self, "截圖", "監控截圖已儲存 (Ctrl+S) ✓"))

        # Start YOLO
        self.yolo.start()

        self._navigate(0)

    def _navigate(self, idx):
        self.stack.setCurrentIndex(idx)
        self.topbar.set_page(self._page_names[idx])
        self.nav.navigate_to(idx)

    def _refresh(self):
        QMessageBox.information(self, "刷新", "頁面數據已刷新 (F5) ✓")

    def closeEvent(self, e):
        self.yolo.stop()
        super().closeEvent(e)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Meta Farm")
    app.setApplicationVersion("2.4.1")

    # Global stylesheet
    app.setStyleSheet(f"""
        QScrollBar:vertical {{
            background:{Theme.BG};
            width:6px;
            margin:0;
        }}
        QScrollBar::handle:vertical {{
            background:{Theme.WOOD_DARK};
            border-radius:3px;
            min-height:30px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        QScrollBar:horizontal {{
            background:{Theme.BG};
            height:6px;
        }}
        QScrollBar::handle:horizontal {{
            background:{Theme.WOOD_DARK};
            border-radius:3px;
        }}
        QToolTip {{
            background:{Theme.BG_NAV};
            color:white;
            border:none;
            padding:6px 10px;
            border-radius:6px;
            font-size:12px;
        }}
        QMessageBox {{
            background:{Theme.BG};
            font-family:'{Theme.FONT_BODY}';
        }}
        QDialog {{
            background:{Theme.BG};
            font-family:'{Theme.FONT_BODY}';
        }}
    """)

    window = MetaFarmApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
