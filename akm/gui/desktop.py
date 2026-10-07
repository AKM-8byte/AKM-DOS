"""Figma AKM Desktop with shared Core and reusable native desktop windows."""
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QLineEdit, QMenu, QPlainTextEdit,
                               QPushButton, QVBoxLayout, QWidget, QWidgetAction)

from main import AKMShell
from .windows import WindowManager
from .terminal import TerminalContent
from .settings_view import SettingsContent

STYLE = '''
QWidget { color: #e8ebe5; background: transparent; font-family: "IBM Plex Mono", Consolas; font-size: 14px; }
QPushButton { background: #1c2622; border: 1px solid #33473d; border-radius: 5px; padding: 8px 14px; }
QPushButton:hover { background: #2e4438; border-color: #54c78c; }
QPushButton:focus, QLineEdit:focus { border-color: #54c78c; }
QPushButton:disabled { color: #858f8c; }
QPlainTextEdit, QLineEdit { background: #090a0a; color: #a1d6ad; border: 1px solid #33403b; padding: 8px; }
QLabel { border: none; }
QMenu { background: #1f2925; color: #e8ebe5; border: 1px solid #384d42; }
QMenu::item:selected { background: #2e7557; }
'''


class Workspace(WindowManager):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#161f1c'))
        painter.fillRect(0, round(self.height() * 520 / 740), self.width(), self.height(), QColor('#0e1211'))


class Desktop(QWidget):
    def __init__(self, core, parent=None, display=None):
        super().__init__(parent)
        if not core.started:
            raise ValueError('Desktop requires a successfully started Core.')
        self.core = core
        self.display = display
        self.shell = AKMShell(core=core)
        self.setStyleSheet(STYLE)
        self.manager = Workspace(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.manager, 1)
        self.resize(1280, 800)
        self.manager.resize(1280, 740)
        self.brand = QLabel('AKM', self.manager)
        self.brand.setGeometry(50, 42, 250, 42)
        self.brand.setStyleSheet('color: #bdccbf; font-size: 32px; font-weight: bold;')
        self.subtitle = QLabel('DOS 0.8', self.manager)
        self.subtitle.setGeometry(52, 82, 200, 20)
        self.subtitle.setStyleSheet('color: #54c78c; font-size: 12px;')
        self.app_buttons = {}
        for index, (title, key) in enumerate([('TERMINAL', 'terminal'), ('FILES', 'files'), ('SYSTEM', 'system'), ('NOTES', 'notes')]):
            button = QPushButton('', self.manager)
            button.setGeometry(50, 150 + 100 * index, 58, 58)
            button.setAccessibleName(title)
            button.setToolTip(title)
            button.setStyleSheet('background: #1c2521; border: 1px solid #384d42; border-radius: 8px;')
            caption = QLabel(title, self.manager)
            caption.setGeometry(50, 218 + 100 * index, 170, 20)
            caption.setStyleSheet('font-size: 12px;')
            if key in {'files', 'notes'}:
                button.setEnabled(False)
                button.setToolTip('Mevcut uygulamaya Shell üzerinden erişilebilir; bu Desktop penceresi henüz eklenmedi.')
            else:
                button.clicked.connect(lambda checked=False, value=key: self.open_app(value))
            self.app_buttons[key] = button
        self.taskbar = QWidget(self)
        self.taskbar.setFixedHeight(60)
        self.taskbar.setObjectName('taskbar')
        self.taskbar.setStyleSheet('QWidget#taskbar { background: #090b0b; }')
        layout.addWidget(self.taskbar)
        bar = QHBoxLayout(self.taskbar)
        bar.setContentsMargins(18, 10, 26, 10)
        bar.setSpacing(24)
        self.start_button = QPushButton('◈  AKM')
        self.start_button.setFixedSize(124, 38)
        self.start_button.clicked.connect(self.show_menu)
        bar.addWidget(self.start_button)
        self.tasks = QHBoxLayout()
        self.tasks.setSpacing(8)
        bar.addLayout(self.tasks)
        self.task_buttons = {}
        bar.addStretch()
        self.clock = QLabel('')
        self.clock.setStyleSheet('font-size: 12px;')
        bar.addWidget(self.clock)
        self.manager.changed.connect(self.refresh_tasks)
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()
        # First live example matches the terminal window in the Figma frame.
        self.open_app('terminal')

    @property
    def terminal(self):
        return self.open_app('terminal').content.output

    @property
    def command_input(self):
        return self.open_app('terminal').content.command_input

    def update_clock(self):
        self.clock.setText(datetime.now().strftime('%H:%M   %d.%m.%Y'))

    def open_app(self, key):
        if key == 'terminal':
            def factory():
                content = TerminalContent(self.core, self.shell)
                content.exit_requested.connect(lambda: self.window().close())
                content.menu_requested.connect(self.show_menu)
                return content
            window = self.manager.open(key, 'AKM Terminal', factory)
            window.content.command_input.setFocus()
            return window
        if key == 'settings':
            return self.manager.open(key, 'Settings / Display', lambda: SettingsContent(self.core, self.display))
        if key == 'system':
            def factory():
                content = QPlainTextEdit()
                content.setReadOnly(True)
                info = self.core.platform.system_info()
                rows = [f'AKM DOS 0.8 / {self.core.username}', '', *[f'{k}: {v}' for k, v in info.items()], '',
                        *[f'{k.upper()}: {v.upper()}' for k, v in self.core.service_status.items()], '',
                        'Dosya modeli: AKM:/', 'CPU/RAM/disk kullanım ölçümü sağlanmıyor.']
                content.setPlainText('\n'.join(rows))
                return content
            return self.manager.open(key, 'AKM System', factory)
        raise ValueError(f'Unsupported Desktop app: {key}')

    def show_view(self, target):
        return self.open_app({'TERM': 'terminal', 'CORE': 'system', 'CFG': 'settings'}[target])

    def execute_command(self, raw):
        # Preserve the previous quick-command adapter and its Shell semantics.
        views = {'terminal': 'terminal', 'ayarlar': 'settings', 'core': 'system'}
        if raw.strip().casefold() in views:
            self.open_app(views[raw.strip().casefold()])
        else:
            self.open_app('terminal').content.execute(raw)

    def show_menu(self):
        menu = QMenu(self)
        search = QLineEdit()
        search.setPlaceholderText('Uygulama ara…')
        search_action = QWidgetAction(menu)
        search_action.setDefaultWidget(search)
        menu.addAction(search_action)
        app_actions = {}
        for title, key in [('Terminal', 'terminal'), ('System', 'system'), ('Settings / Display', 'settings')]:
            action = menu.addAction(title)
            action.triggered.connect(lambda checked=False, value=key: self.open_app(value))
            app_actions[title] = action
        search.textChanged.connect(lambda query: [action.setVisible(query.casefold() in title.casefold()) for title, action in app_actions.items()])
        menu.addSeparator()
        menu.addAction('Çıkış', lambda: self.window().close())
        self.menu = menu
        menu.popup(self.start_button.mapToGlobal(self.start_button.rect().topLeft()))
        search.setFocus()

    def refresh_tasks(self):
        for key in list(self.task_buttons):
            if key not in self.manager.windows:
                button = self.task_buttons.pop(key)
                self.tasks.removeWidget(button)
                button.deleteLater()
        for key, window in self.manager.windows.items():
            if key not in self.task_buttons:
                button = QPushButton()
                button.clicked.connect(lambda checked=False, value=key: self.manager.windows[value].restore())
                self.tasks.addWidget(button)
                self.task_buttons[key] = button
            button = self.task_buttons[key]
            button.setText(f'[ {key.upper()} ]')
            button.setToolTip('Restore' if window.minimized else window.title)
            color = '#54c78c' if self.manager.active_key == key and not window.minimized else '#858f8c'
            button.setStyleSheet(f'color: {color}; border: none; background: transparent; font-size: 13px; padding: 0;')

    def show_audio_warning(self, message):
        self.subtitle.setToolTip(message)
        self.subtitle.setText('DOS 0.8 · Ses uyarısı')
