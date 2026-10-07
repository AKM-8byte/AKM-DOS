"""Presentation-only fullscreen policy backed by the existing SettingsService."""
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

DISPLAY_KEY = 'gui.display_mode'
MODES = ('fullscreen', 'window')


class DisplaySettings(QObject):
    changed = Signal(str)

    def __init__(self, settings, host):
        super().__init__(host)
        self.settings = settings
        self.host = host

    @property
    def mode(self):
        value = self.settings.get(DISPLAY_KEY)
        return value if value in MODES else None

    def apply(self):
        if self.mode == 'fullscreen':
            self.host.showFullScreen()
        elif self.mode == 'window':
            self.host.showNormal()

    def select(self, mode):
        if mode not in MODES:
            raise ValueError('Geçersiz ekran modu.')
        # Apply only after the atomic write succeeds.
        self.settings.set(DISPLAY_KEY, mode)
        self.apply()
        self.changed.emit(mode)


class DisplayModeDialog(QDialog):
    def __init__(self, display):
        super().__init__(display.host)
        self.display = display
        self.setWindowTitle('AKM DOS / Ekran modu')
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.resize(480, 220)
        self.setStyleSheet('''
            QDialog { background: #0e1111; color: #e8ebe5; }
            QLabel { color: #e8ebe5; background: transparent; }
            QPushButton { background: #1c2622; border: 1px solid #33473d; color: #e8ebe5; padding: 10px; border-radius: 6px; }
            QPushButton:hover { background: #2e7557; }
        ''')
        layout = QVBoxLayout(self)
        self.question = QLabel("AKM DOS'u tam ekran çalıştırmak ister misiniz?")
        self.question.setWordWrap(True)
        layout.addWidget(self.question)
        self.error = QLabel('')
        self.error.setWordWrap(True)
        layout.addWidget(self.error)
        self.fullscreen_button = QPushButton('Tam Ekran')
        self.window_button = QPushButton('Pencere Modu')
        self.fullscreen_button.clicked.connect(lambda: self.choose('fullscreen'))
        self.window_button.clicked.connect(lambda: self.choose('window'))
        layout.addWidget(self.fullscreen_button)
        layout.addWidget(self.window_button)

    def choose(self, mode):
        try:
            self.display.select(mode)
        except Exception as exc:
            self.error.setText(f'Tercih kaydedilemedi: {exc}')
            return
        self.accept()
