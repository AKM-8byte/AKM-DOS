"""Display preferences are saved through the shared SettingsService."""
from PySide6.QtWidgets import QLabel, QPushButton, QPlainTextEdit, QVBoxLayout, QWidget


class SettingsContent(QWidget):
    def __init__(self, core, display):
        super().__init__()
        self.core = core
        self.display = display
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(QLabel('Ekran modu'))
        self.current = QLabel('')
        layout.addWidget(self.current)
        for text, mode in [('Tam Ekran', 'fullscreen'), ('Pencere Modu', 'window')]:
            button = QPushButton(text)
            button.setEnabled(display is not None)
            button.clicked.connect(lambda checked=False, value=mode: self.select(value))
            layout.addWidget(button)
        self.error = QLabel('')
        self.error.setWordWrap(True)
        layout.addWidget(self.error)
        self.values = QPlainTextEdit()
        self.values.setReadOnly(True)
        layout.addWidget(self.values, 1)
        self.refresh()
        if display:
            display.changed.connect(self.refresh)

    def refresh(self, *_):
        mode = self.display.mode if self.display else None
        self.current.setText('Tam Ekran' if mode == 'fullscreen' else 'Pencere Modu' if mode == 'window' else 'Tercih seçilmedi')
        self.values.setPlainText('\n'.join(f'{key}: {value}' for key, value in self.core.settings.all().items()))

    def select(self, mode):
        try:
            self.display.select(mode)
            self.error.clear()
        except Exception as exc:
            self.error.setText(f'Ayar kaydedilemedi: {exc}')
