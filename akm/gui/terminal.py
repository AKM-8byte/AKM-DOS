"""Window content adapter for the existing AKMShell; no second command engine."""
import contextlib
import io

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget

from main import AKMShell
from akm.version import VERSION


class TerminalContent(QWidget):
    exit_requested = Signal()
    menu_requested = Signal()

    def __init__(self, core, shell=None):
        super().__init__()
        self.core = core
        self.shell = shell or AKMShell(core=core)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 22)
        layout.setSpacing(12)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(40)
        self.output.setStyleSheet('background: #090a0a; color: #a1d6ad; font-family: "IBM Plex Mono", Consolas; font-size: 16px; border: none; padding: 0;')
        self.output.setPlainText(f'AKM DOS [Version {VERSION}]\nCore services initialized successfully.\n\n{self.shell.prompt()}status\n' + self.status_text())
        layout.addWidget(self.output)
        row = QHBoxLayout()
        self.prompt = QLabel(self.shell.prompt())
        self.prompt.setStyleSheet('color: #a1d6ad; font-family: Consolas; font-size: 14px;')
        row.addWidget(self.prompt)
        self.command_input = QLineEdit()
        self.command_input.setAccessibleName('Terminal komutu')
        self.command_input.setStyleSheet('background: #090a0a; color: #a1d6ad; border: none; font-family: Consolas; font-size: 16px; padding: 0;')
        self.command_input.returnPressed.connect(lambda: self.execute(self.command_input.text()))
        row.addWidget(self.command_input, 1)
        layout.addLayout(row)
        layout.addStretch(1)
        self.setFocusProxy(self.command_input)
        self.output.textChanged.connect(self.fit_output)

    def fit_output(self):
        # Place the live prompt after the text, like the reference terminal.
        # Longer histories scroll within the available window height.
        wanted = self.output.document().blockCount() * self.output.fontMetrics().height() + 12
        available = max(60, self.height() - 100)
        self.output.setMaximumHeight(min(wanted, available))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_output()

    def status_text(self):
        rows = [('CORE', 'ready' if self.core.started else 'not_started')]
        rows.extend((key.upper(), value) for key, value in self.core.service_status.items())
        return '\n'.join(f'{key:12} {value.upper()}' for key, value in rows)

    def execute(self, raw):
        raw = raw.strip()
        self.command_input.clear()
        if not raw:
            return
        if raw == '/':
            self.menu_requested.emit()
            return
        allowed = {'sürüm', 'version', 'pwd', 'dir', 'ls', 'cd', 'mkdir', 'touch',
                   'type', 'cat', 'sil', 'del', 'settings', 'systeminfo'}
        command, *rest = raw.split(maxsplit=1)
        command = command.lower()
        self.output.appendPlainText(f'\n{self.shell.prompt()}{raw}')
        if command in {'yardım', 'help'}:
            self.output.appendPlainText('Desktop komutları: ' + ', '.join(sorted(allowed)) + ', status, temizle, çıkış')
        elif command == 'status':
            self.output.appendPlainText(self.status_text())
        elif command in {'temizle', 'clear'}:
            self.output.clear()
        elif command in {'çıkış', 'kapat', 'exit'}:
            self.exit_requested.emit()
        elif command not in allowed:
            self.output.appendPlainText('Bu komut Desktop içinde desteklenmiyor. yardım yazın.')
        else:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                try:
                    self.shell.commands[command](rest[0] if rest else '')
                except Exception as exc:
                    self.shell._log_error(exc)
                    print(f'Hata: {exc}')
            self.output.appendPlainText(output.getvalue().rstrip())
        self.prompt.setText(self.shell.prompt())
