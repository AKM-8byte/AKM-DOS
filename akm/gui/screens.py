"""Figma BIOS/POST and Boot/Login screens using native Qt content."""
from pathlib import Path

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QFrame, QGraphicsScene, QGraphicsView, QLabel,
                               QLineEdit, QPushButton, QWidget)

ASSETS = Path(__file__).resolve().parents[2] / 'assets/redesign'


def text(parent, value, rect, size=16, color='#e8ebe5', bold=False, mono=True):
    result = QLabel(value, parent)
    result.setGeometry(*rect)
    family = '"IBM Plex Mono", Consolas' if mono else 'Inter, "Segoe UI"'
    result.setStyleSheet(f'background: transparent; border: none; color: {color}; font-family: {family}; font-size: {size}px; font-weight: {700 if bold else 400};')
    return result


class ArtboardView(QGraphicsView):
    def __init__(self, canvas, background, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        canvas.setFixedSize(1280, 800)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor(background))
        self.model = QGraphicsScene(self)
        self.model.setSceneRect(0, 0, 1280, 800)
        self.setScene(self.model)

    def mount(self):
        self.model.addWidget(self.canvas)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.model.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class BiosPage(ArtboardView):
    continue_requested = Signal()
    retry_requested = Signal()

    def __init__(self):
        canvas = QWidget()
        canvas.setStyleSheet('background: #00146b;')
        super().__init__(canvas, '#00146b')
        text(canvas, 'AKM SYSTEM BIOS 0.8', (42, 32, 750, 36), 24, bold=True)
        text(canvas, 'Copyright (C) 2026 AKM Systems', (42, 66, 700, 25), 16, '#b8b8b8')
        rule = QFrame(canvas)
        rule.setGeometry(42, 100, 1196, 2)
        rule.setStyleSheet('background: #b8b8b8;')
        self.post = text(canvas, '', (42, 130, 800, 520), 18)
        self.post.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.side = text(canvas, '', (900, 130, 335, 330), 16, '#dbd9c4')
        self.side.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.message = text(canvas, 'Core kurulumu bekleniyor.', (42, 650, 1196, 78), 16)
        self.message.setWordWrap(True)
        footer = QFrame(canvas)
        footer.setGeometry(0, 742, 1280, 58)
        footer.setStyleSheet('background: #b3b3b3;')
        text(footer, 'AKM Core POST  |  Gerçek servis durumları', (26, 17, 800, 25), 15, '#05081f', True)
        self.continue_button = QPushButton('Boot / Login →', footer)
        self.continue_button.setGeometry(980, 10, 260, 38)
        self.continue_button.setStyleSheet('color: #05081f; border: 1px solid #555; background: #b3b3b3; font-family: Consolas; font-size: 16px;')
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(self.continue_requested)
        self.retry_button = QPushButton('Yeniden dene', canvas)
        self.retry_button.setGeometry(900, 550, 300, 46)
        self.retry_button.setStyleSheet('background: #00146b; color: #e8ebe5; border: 1px solid #b8b8b8; font-family: Consolas; padding: 8px;')
        self.retry_button.clicked.connect(self.retry_requested)
        self.retry_button.hide()
        self.update_status({}, {}, False)
        self.mount()

    def update_status(self, info, services, started):
        rows = ['AKM BIOS Revision 0.8', '', f'Platform          : {info.get("system", "alınamadı")} {info.get("release", "")}',
                f'Makine            : {info.get("machine", "alınamadı")}',
                f'Python            : {info.get("python", "alınamadı")}',
                'Bellek ölçümü     : sağlanmıyor', 'Dosya modeli      : AKM:/', '',
                f'AKM Core          : {"READY" if started else "NOT_STARTED"}']
        rows.extend(f'{key.upper():18}: {value.upper()}' for key, value in services.items())
        self.post.setText('\n'.join(rows))
        self.side.setText('SYSTEM INFORMATION\n------------------\nBoot Mode : Windows host\nCore      : AKMCore\nShell     : ' + ('Ready' if started else 'Login bekleniyor') + '\nGUI       : PySide6')


class LoginBackground(QWidget):
    def __init__(self):
        super().__init__()
        self.layers = []
        slots = [(-50, 480, 80), (160, 430, 130), (370, 465, 95), (580, 380, 180),
                 (790, 445, 115), (1000, 410, 150), (1210, 460, 100)]
        for index, (x, y, height) in enumerate(slots):
            svg = QSvgRenderer(str(ASSETS / f'login-mountain-{index}.svg'), self)
            if not svg.isValid():
                raise ValueError(f'Login görseli yüklenemedi: mountain-{index}')
            self.layers.append((svg, QRectF(x + 20.096, y, 259.808, height * 0.75)))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#060809'))
        painter.fillRect(0, 0, 1280, 220, QColor('#091312'))
        painter.fillRect(0, 560, 1280, 240, QColor('#090b0b'))
        for svg, rect in self.layers:
            svg.render(painter, rect)


class LoginPage(ArtboardView):
    login_requested = Signal()
    display_requested = Signal()

    def __init__(self):
        canvas = LoginBackground()
        super().__init__(canvas, '#060809')
        text(canvas, 'AKM', (78, 72, 500, 60), 44, bold=True)
        text(canvas, 'DOS / 0.8', (80, 126, 500, 25), 14, '#54c78c')
        text(canvas, 'A quiet system, ready when you are.', (80, 210, 650, 32), 17, '#858f8c')
        panel = QFrame(canvas)
        panel.setGeometry(760, 150, 410, 500)
        panel.setStyleSheet('QFrame { background: #0e1111; border: 1px solid #293330; border-radius: 12px; }')
        text(panel, 'WELCOME', (44, 52, 322, 22), 14, '#54c78c', True)
        self.user_title = text(panel, 'Yerel kullanıcı', (44, 95, 322, 42), 31, bold=True, mono=False)
        self.user_hint = text(panel, 'Local user  •  AKM DOS', (44, 138, 322, 25), 14, '#858f8c', mono=False)
        text(panel, 'KULLANICI', (44, 210, 322, 22), 12, '#858f8c', True)
        self.username = QLineEdit(panel)
        self.username.setGeometry(44, 236, 322, 50)
        self.username.setPlaceholderText('İlk açılış için kullanıcı adı')
        self.username.setAccessibleName('Yerel kullanıcı adı')
        self.username.setStyleSheet('background: #090b0b; border: 1px solid #33423d; border-radius: 6px; color: #e8ebe5; font-family: Consolas; font-size: 18px; padding: 12px;')
        self.username.returnPressed.connect(self.login_requested)
        self.login_button = QPushButton('ENTER SYSTEM  →', panel)
        self.login_button.setGeometry(44, 318, 322, 54)
        self.login_button.setStyleSheet('background: #2e7557; color: #e8ebe5; border: none; border-radius: 6px; font-family: Consolas; font-size: 15px; font-weight: bold;')
        self.login_button.clicked.connect(self.login_requested)
        self.error = text(panel, '', (44, 388, 322, 85), 12, '#858f8c', mono=False)
        self.error.setWordWrap(True)
        line = QFrame(canvas)
        line.setGeometry(80, 712, 600, 2)
        line.setStyleSheet('background: #2e7557;')
        self.status = text(canvas, '', (80, 735, 900, 40), 12, '#858f8c')
        self.display_button = QPushButton('Ekran modu', canvas)
        self.display_button.setGeometry(1010, 730, 160, 44)
        self.display_button.setStyleSheet('background: #0e1111; color: #858f8c; border: 1px solid #293330; border-radius: 6px; font-family: Consolas;')
        self.display_button.clicked.connect(self.display_requested)
        self.mount()

    def set_user(self, username):
        self.username.setText(username)
        self.username.setReadOnly(bool(username))
        self.user_title.setText(username or 'İlk açılış')
        self.user_title.setToolTip(username)
        self.user_hint.setText('Local user  •  AKM DOS' if username else 'Yerel kullanıcı adınızı girin')
        self.error.setText('Yerel oturum parola doğrulaması kullanmaz.')

    def update_status(self, services, started):
        self.status.setText(f'CORE {"READY" if started else "NOT_STARTED"}  /  FILESYSTEM {services.get("filesystem", "not_started").upper()}  /  PLATFORM {services.get("platform", "not_started").upper()}')
