"""Reusable, bounded in-desktop windows. No Core or platform dependency."""
from PySide6.QtCore import QEvent, QRect, Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class TitleBar(QFrame):
    def __init__(self, window, title):
        super().__init__(window)
        self.owner = window
        self.anchor = None
        self.setFixedHeight(42)
        self.setObjectName('titlebar')
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 10, 0)
        caption = QLabel(title)
        caption.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(caption, 1)
        for glyph, name, action in [('_', 'Minimize', window.minimize), ('□', 'Maximize / Restore', window.toggle_maximize), ('×', 'Close', window.close_window)]:
            button = QPushButton(glyph)
            button.setAccessibleName(name)
            button.setToolTip(name)
            button.setFixedSize(26, 28)
            button.clicked.connect(action)
            layout.addWidget(button)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.owner.manager.activate(self.owner)
            if not self.owner.maximized:
                self.anchor = event.globalPosition().toPoint() - self.owner.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.anchor is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.owner.move_bounded(event.globalPosition().toPoint() - self.anchor)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.anchor = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.anchor = None
            self.owner.toggle_maximize()


class BaseWindow(QFrame):
    def __init__(self, manager, key, title, content):
        super().__init__(manager)
        self.manager, self.key, self.title = manager, key, title
        self.minimized = False
        self.maximized = False
        self.restore_geometry = None
        self.setObjectName('akmwindow')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet('''
            QFrame#akmwindow { background: #090a0a; border: 1px solid #33403b; border-radius: 8px; }
            QFrame#titlebar { background: #1f2925; border: none; border-radius: 7px; }
            QFrame#titlebar QLabel { color: #e8ebe5; font-family: "IBM Plex Mono", Consolas; font-size: 14px; font-weight: bold; background: transparent; }
            QFrame#titlebar QPushButton { background: transparent; color: #858f8c; border: none; padding: 0; font-size: 15px; }
            QFrame#titlebar QPushButton:hover { background: #33403b; color: #e8ebe5; }
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        self.titlebar = TitleBar(self, title)
        layout.addWidget(self.titlebar)
        self.content = content
        layout.addWidget(content, 1)
        for widget in [self, *self.findChildren(QWidget)]:
            widget.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            self.manager.activate(self)
        return super().eventFilter(watched, event)

    def move_bounded(self, position):
        bounds = self.manager.rect()
        x = max(0, min(position.x(), max(0, bounds.width() - self.width())))
        y = max(0, min(position.y(), max(0, bounds.height() - self.height())))
        self.move(x, y)

    def constrain(self):
        if self.maximized:
            self.setGeometry(self.manager.rect())
        else:
            self.resize(min(self.width(), self.manager.width()), min(self.height(), self.manager.height()))
            self.move_bounded(self.pos())

    def minimize(self):
        self.minimized = True
        self.hide()
        if self.manager.active_key == self.key:
            self.manager.active_key = next((key for key, window in reversed(list(self.manager.windows.items())) if not window.minimized), None)
            if self.manager.active_key:
                self.manager.windows[self.manager.active_key].raise_()
        self.manager.changed.emit()

    def restore(self):
        self.minimized = False
        self.constrain()
        self.show()
        self.manager.activate(self)
        self.content.setFocus()

    def toggle_maximize(self):
        if self.maximized:
            self.maximized = False
            self.setGeometry(self.restore_geometry)
        else:
            self.restore_geometry = QRect(self.geometry())
            self.maximized = True
        self.constrain()
        self.manager.activate(self)

    def close_window(self):
        self.manager.remove(self.key)

    def closeEvent(self, event):
        self.manager.remove(self.key)
        event.accept()


class WindowManager(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.windows = {}
        self.active_key = None

    def open(self, key, title, content_factory, geometry=QRect(285, 125, 820, 500)):
        if key in self.windows:
            self.windows[key].restore()
            return self.windows[key]
        window = BaseWindow(self, key, title, content_factory())
        window.setGeometry(geometry)
        window.constrain()
        self.windows[key] = window
        window.show()
        self.activate(window)
        return window

    def activate(self, window):
        if self.windows.get(window.key) is not window:
            return
        self.active_key = window.key
        window.raise_()
        self.changed.emit()

    def remove(self, key):
        window = self.windows.pop(key, None)
        if window is None:
            return
        window.hide()
        window.deleteLater()
        if self.active_key == key:
            self.active_key = next((k for k, w in reversed(list(self.windows.items())) if not w.minimized), None)
            if self.active_key:
                self.windows[self.active_key].raise_()
        self.changed.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for window in self.windows.values():
            window.constrain()
