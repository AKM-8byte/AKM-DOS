"""Render isolated redesign screens with temporary data and no audio playback."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtGui import QFontDatabase
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QWidget
from akm.gui.boot import BootSession
from akm.gui.desktop import Desktop
from akm.gui.screens import BiosPage, LoginPage
from akm.gui.display import DisplaySettings, DisplayModeDialog


def main():
    app = QApplication([])
    font_dir = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    for name in ('segoeui.ttf', 'segoeuib.ttf', 'seguisym.ttf', 'consola.ttf', 'consolab.ttf'):
        if (font_dir / name).is_file():
            QFontDatabase.addApplicationFont(str(font_dir / name))
    output = ROOT / 'artifacts/0.8-redesign'
    output.mkdir(parents=True, exist_ok=True)

    def render(widget, name, width=1280, height=800):
        widget.resize(width, height)
        widget.show()
        app.processEvents()
        widget.grab().save(str(output / f'{name}.png'))

    with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as temporary:
        session = BootSession(Path(temporary))
        session.prepare()
        host = QWidget()
        display_dialog = DisplayModeDialog(DisplaySettings(session.prepared_core.settings, host))
        render(display_dialog, 'display-mode', 480, 250)
        display_dialog.close()
        bios = BiosPage()
        bios.update_status(session.system_info, session.service_status, False)
        bios.message.setText('POST tamamlandı. Kullanıcı oturumu Boot / Login ekranında açılacak.')
        bios.continue_button.setEnabled(True)
        render(bios, 'bios')
        core = session.login('Ahmet Kayra')
        login = LoginPage()
        login.set_user(core.username)
        login.update_status(core.service_status, True)
        render(login, 'login')
        desktop = Desktop(core)
        render(desktop, 'desktop')
        render(desktop, 'desktop-small', 960, 600)
        desktop.manager.windows['terminal'].move_bounded(QPoint(120, 80))
        desktop.open_app('system')
        render(desktop, 'windows')
        bios.message.setText('Başlangıç başarısız: Ayar dosyası okunamadı.\nAyarlar sıfırlanmaz. Sorunu giderip yeniden deneyin.')
        bios.continue_button.setEnabled(False)
        bios.retry_button.show()
        render(bios, 'boot-error')
        for widget in (desktop, login, bios):
            widget.close()
    print(f'Preview screens saved: {output}')


if __name__ == '__main__':
    main()
