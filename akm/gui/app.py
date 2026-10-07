"""BIOS -> local login -> Desktop, sharing a single AKMCore."""
from pathlib import Path
import sys

from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import QApplication, QStackedWidget, QVBoxLayout, QWidget

from .boot import BootSession
from .sound import StartupSound
from .desktop import Desktop
from .display import DisplaySettings, DisplayModeDialog
from .screens import BiosPage, LoginPage


class BootWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, session, action, username='', parent=None):
        super().__init__(parent)
        self.session, self.action, self.username = session, action, username

    def run(self):
        try:
            result = self.session.prepare() if self.action == 'prepare' else self.session.login(self.username)
            self.succeeded.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class BootWindow(QWidget):
    def __init__(self, root):
        super().__init__()
        self.root = Path(root)
        self.session = BootSession(root)
        self.worker = None
        self.core = None
        self.desktop = None
        self.display = None
        self.mode_dialog = None
        self.result = None
        self.failure = ''
        self.audio_message = ''
        self.initial_show = True
        self.stage = 'bios'
        self.setWindowTitle('AKM DOS 0.8 / BIOS')
        self.resize(1280, 800)
        self.setMinimumSize(800, 500)
        self.setStyleSheet('''
            QWidget { background: #060809; color: #e8ebe5; font-family: "Segoe UI"; font-size: 14px; }
            QPushButton { background: #1c2622; border: 1px solid #33473d; border-radius: 5px; padding: 10px; }
            QPushButton:hover { background: #2e7557; }
            QPushButton:disabled { color: #858f8c; }
        ''')
        self.stack = QStackedWidget(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)
        self.bios_page = BiosPage()
        self.login_page = None
        self.stack.addWidget(self.bios_page)
        self.bios_page.continue_requested.connect(self.open_login)
        self.bios_page.retry_requested.connect(self.start_bios)
        self.transition = QTimer(self)
        self.transition.setSingleShot(True)
        self.transition.timeout.connect(self.advance)
        self.sound = StartupSound(self.root / 'assets/audio/akm_horizon.wav', self)
        self.sound.warning.connect(self.audio_warning)

    def showEvent(self, event):
        super().showEvent(event)
        if self.initial_show:
            self.initial_show = False
            QTimer.singleShot(0, self.start_bios)

    def start_boot(self):
        self.start_bios()

    def start_bios(self):
        if self.core and self.core.started or self.worker and self.worker.isRunning():
            return
        self.initial_show = False
        self.stage = 'bios'
        self.transition.stop()
        self.stack.setCurrentWidget(self.bios_page)
        self.bios_page.continue_button.setEnabled(False)
        self.bios_page.retry_button.hide()
        self.bios_page.message.setText('AKMCore kuruluyor…')
        self.start_job('prepare')

    def start_job(self, action, username=''):
        if self.worker and self.worker.isRunning():
            return
        self.result = None
        self.failure = ''
        self.worker = BootWorker(self.session, action, username, self)
        self.worker.succeeded.connect(self.receive_result)
        self.worker.failed.connect(self.receive_failure)
        self.worker.finished.connect(self.boot_finished)
        self.worker.start()

    def receive_result(self, result):
        # The GUI does not access the Core until the worker has finished.
        self.result = result

    def receive_failure(self, message):
        self.failure = message

    def boot_finished(self):
        action = self.worker.action
        if self.failure:
            if action == 'prepare':
                self.bios_page.message.setText(f'Başlangıç başarısız: {self.failure}\nSorunu giderip yeniden deneyin. Ayarlar sıfırlanmaz.')
                self.bios_page.retry_button.show()
            else:
                self.login_page.error.setText(f'Oturum açılamadı: {self.failure}')
                self.login_page.login_button.setEnabled(True)
                self.login_page.username.setEnabled(True)
                self.login_page.display_button.setEnabled(True)
                self.login_page.update_status(self.session.service_status, False)
            self.bios_page.update_status(self.session.system_info, self.session.service_status, False)
            return
        if action == 'prepare':
            self.bios_page.update_status(self.session.system_info, self.session.service_status, False)
            self.bios_page.message.setText('POST tamamlandı. Kullanıcı oturumu Boot / Login ekranında açılacak.')
            self.bios_page.continue_button.setEnabled(True)
            if self.display:
                self.display.deleteLater()
            self.display = DisplaySettings(self.result.settings, self)
            if self.display.mode:
                self.display.apply()
            self.transition.start(1000)
        else:
            self.core = self.result
            self.login_page.set_user(self.core.username)
            self.login_page.update_status(self.core.service_status, True)
            self.login_page.error.setText('Oturum hazır. Desktop açılıyor…')
            self.login_page.login_button.setText('MASAÜSTÜNÜ AÇ  →')
            self.login_page.login_button.setEnabled(True)
            self.login_page.display_button.setEnabled(True)
            self.sound.play()
            self.transition.start(4000)

    def advance(self):
        if self.stage == 'bios':
            self.open_login()
        elif self.stage == 'login' and self.core:
            self.open_desktop()

    def open_login(self):
        if self.session.prepared_core is None or self.worker and self.worker.isRunning():
            return
        self.transition.stop()
        try:
            if self.login_page is None:
                self.login_page = LoginPage()
                self.stack.addWidget(self.login_page)
                self.login_page.login_requested.connect(self.login)
                self.login_page.display_requested.connect(self.choose_display_mode)
            self.login_page.set_user(self.session.suggested_username)
            self.login_page.update_status(self.session.service_status, False)
            self.login_page.login_button.setText('ENTER SYSTEM  →')
            self.login_page.login_button.setEnabled(True)
        except Exception as exc:
            self.bios_page.message.setText(f'Login ekranı açılamadı: {exc}')
            return
        self.stage = 'login'
        self.stack.setCurrentWidget(self.login_page)
        self.setWindowTitle('AKM DOS 0.8 / Boot & Login')
        if self.display.mode is None:
            self.choose_display_mode()

    def choose_display_mode(self):
        if self.display is None or self.worker and self.worker.isRunning():
            return
        if self.mode_dialog and self.mode_dialog.isVisible():
            self.mode_dialog.raise_()
            return
        self.mode_dialog = DisplayModeDialog(self.display)
        self.mode_dialog.open()

    def login(self):
        if self.worker and self.worker.isRunning():
            return
        if self.core and self.core.started:
            self.open_desktop()
            return
        if self.display.mode is None:
            self.choose_display_mode()
            return
        self.login_page.username.setEnabled(False)
        self.login_page.login_button.setEnabled(False)
        self.login_page.display_button.setEnabled(False)
        self.login_page.error.setText('Kullanıcı oturumu ve FileSystem başlatılıyor…')
        self.start_job('login', self.login_page.username.text())

    def open_desktop(self):
        if not self.core or not self.core.started or self.desktop is not None:
            return
        if self.worker and self.worker.isRunning() or self.display.mode is None:
            return
        self.transition.stop()
        try:
            self.desktop = Desktop(self.core, self, self.display)
        except Exception as exc:
            self.login_page.error.setText(f'Desktop açılamadı: {exc}')
            self.sound.stop()
            return
        if self.audio_message:
            self.desktop.show_audio_warning(self.audio_message)
        self.stack.addWidget(self.desktop)
        self.stack.setCurrentWidget(self.desktop)
        self.stage = 'desktop'
        self.setWindowTitle('AKM DOS 0.8 / Desktop')

    def audio_warning(self, message):
        self.audio_message = message
        if self.desktop:
            self.desktop.show_audio_warning(message)
        elif self.login_page:
            self.login_page.error.setText(message)

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            event.ignore()
        else:
            self.transition.stop()
            self.sound.stop()
            event.accept()


def run(root: Path) -> int:
    app = QApplication(sys.argv)
    window = BootWindow(root)
    window.show()
    return app.exec()
