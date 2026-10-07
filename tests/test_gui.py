"""Qt integration checks: temporary data, real window controls, no audio playback."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QPushButton
    from akm.gui.app import BootWindow
    from akm.gui.desktop import Desktop
    from akm.gui.display import DISPLAY_KEY, DisplaySettings
    from akm.gui.sound import StartupSound
except ModuleNotFoundError:
    QApplication = None


@unittest.skipIf(QApplication is None, 'PySide6 optional GUI dependency not installed')
class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.window = BootWindow(self.root)
        self.addCleanup(self.window.deleteLater)
        self.addCleanup(self.window.close)
        self.real_sound_play = StartupSound.play
        sound = patch.object(StartupSound, 'play')
        self.sound_play = sound.start()
        self.addCleanup(sound.stop)

    def wait_worker(self):
        deadline = time.monotonic() + 5
        while not self.window.worker.isFinished() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.01)
        self.assertTrue(self.window.worker.isFinished())
        self.app.processEvents()

    def post(self):
        self.window.start_bios()
        self.wait_worker()
        self.window.open_login()
        self.app.processEvents()

    def login(self):
        self.post()
        self.window.mode_dialog.choose('window')
        self.window.login_page.username.setText('Test User')
        self.window.login()
        self.wait_worker()

    def desktop(self):
        self.login()
        self.window.open_desktop()
        self.window.show()
        self.app.processEvents()
        return self.window.desktop

    def test_bios_login_desktop_transfers_same_core(self):
        self.post()
        prepared = self.window.session.prepared_core
        self.assertEqual(self.window.stage, 'login')
        self.assertFalse(prepared.started)
        self.assertIn('FILESYSTEM NOT_STARTED', self.window.login_page.status.text())
        self.assertIn('NOT_STARTED', self.window.bios_page.post.text())
        self.window.mode_dialog.choose('window')
        self.window.login_page.username.setText('Ahmet')
        self.window.login()
        self.wait_worker()
        self.assertIs(self.window.core, prepared)
        self.assertIn('FILESYSTEM READY', self.window.login_page.status.text())
        self.sound_play.assert_called_once()
        self.window.open_desktop()
        desktop = self.window.desktop
        self.assertIs(desktop.core, prepared)
        self.window.open_desktop()
        self.assertIs(self.window.desktop, desktop)

    def test_saved_user_login_ignores_replacement_name(self):
        from akm import AKMCore
        original = AKMCore(self.root)
        original.start('Saved')
        original.settings.set(DISPLAY_KEY, 'window')
        self.post()
        self.assertIsNone(self.window.mode_dialog)
        self.assertTrue(self.window.login_page.username.isReadOnly())
        self.window.login_page.username.setText('Other')
        self.window.login()
        self.wait_worker()
        self.assertEqual(self.window.core.username, 'Saved')

    def test_corrupt_settings_cannot_transition_and_can_retry(self):
        data = self.root / 'Data'
        data.mkdir()
        settings = data / 'settings.json'
        settings.write_text('{broken')
        self.window.start_bios()
        self.wait_worker()
        self.window.open_login()
        self.assertIsNone(self.window.login_page)
        self.assertIn('başarısız', self.window.bios_page.message.text())
        self.assertEqual(settings.read_text(), '{broken')
        self.sound_play.assert_not_called()
        settings.write_text('{}')
        self.post()
        self.assertIsNotNone(self.window.login_page)

    def test_login_service_error_keeps_desktop_closed(self):
        self.post()
        self.window.mode_dialog.choose('window')
        self.window.login_page.username.setText('User')
        with patch.object(self.window.session.prepared_core.platform, 'discover_drives', side_effect=OSError('disk failure')):
            self.window.login()
            self.wait_worker()
        self.assertIsNone(self.window.desktop)
        self.assertIn('PLATFORM FAILED', self.window.login_page.status.text())
        self.assertTrue(self.window.login_page.login_button.isEnabled())
        self.window.login()
        self.wait_worker()
        self.assertTrue(self.window.core.started)

    def test_first_run_mode_prompt_and_saved_preference(self):
        self.post()
        self.assertTrue(self.window.mode_dialog.isVisible())
        self.assertEqual(self.window.mode_dialog.windowTitle(), 'AKM DOS / Ekran modu')
        self.window.mode_dialog.choose('fullscreen')
        self.assertTrue(self.window.isFullScreen())
        self.assertEqual(self.window.display.mode, 'fullscreen')
        self.window.close()
        other = BootWindow(self.root)
        self.addCleanup(other.deleteLater)
        self.addCleanup(other.close)
        other.initial_show = False
        other.start_bios()
        deadline = time.monotonic() + 5
        while not other.worker.isFinished() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.01)
        self.app.processEvents()
        other.open_login()
        self.assertIsNone(other.mode_dialog)
        self.assertTrue(other.isFullScreen())
        other.display.select('window')
        self.assertFalse(other.isFullScreen())

    def test_display_write_failure_does_not_change_window_state(self):
        self.post()
        with patch.object(self.window.display.settings, 'set', side_effect=PermissionError('read-only')):
            self.window.mode_dialog.choose('fullscreen')
        self.assertIsNone(self.window.display.mode)
        self.assertFalse(self.window.isFullScreen())
        self.assertTrue(self.window.mode_dialog.isVisible())
        self.assertIn('kaydedilemedi', self.window.mode_dialog.error.text())

    def test_settings_can_change_display_mode(self):
        desktop = self.desktop()
        settings = desktop.open_app('settings').content
        settings.select('fullscreen')
        self.assertTrue(self.window.isFullScreen())
        self.assertEqual(self.window.core.settings.get(DISPLAY_KEY), 'fullscreen')
        settings.select('window')
        self.assertFalse(self.window.isFullScreen())
        self.assertEqual(self.window.core.settings.get(DISPLAY_KEY), 'window')

    def test_reset_mode_requires_choice_again(self):
        self.post()
        self.window.mode_dialog.choose('window')
        self.window.display.settings.set(DISPLAY_KEY, None)
        self.window.open_login()
        self.assertTrue(self.window.mode_dialog.isVisible())
        self.assertIsNone(self.window.display.mode)

    def test_terminal_shared_filesystem_and_protection(self):
        desktop = self.desktop()
        desktop.execute_command('touch proof.txt')
        self.assertTrue((desktop.core.filesystem.home / 'proof.txt').is_file())
        desktop.execute_command('touch AKM:/System/forbidden.txt')
        self.assertFalse((self.root / 'Data/System/forbidden.txt').exists())
        desktop.execute_command('pwd')
        self.assertIn('AKM:/User', desktop.terminal.toPlainText())
        desktop.execute_command('settings set user.name Other')
        self.assertEqual(desktop.core.settings.get('user.name'), 'Test User')

    def test_terminal_opens_from_desktop_and_close_reopens(self):
        desktop = self.desktop()
        desktop.manager.windows['terminal'].close_window()
        self.assertNotIn('terminal', desktop.manager.windows)
        desktop.app_buttons['terminal'].click()
        terminal = desktop.manager.windows['terminal']
        self.assertIs(terminal.content.core, desktop.core)
        self.assertIs(terminal.content.shell, desktop.shell)

    def test_drag_minimize_restore_maximize_and_close_controls(self):
        desktop = self.desktop()
        window = desktop.manager.windows['terminal']
        original = window.pos()
        bar = window.titlebar
        QTest.mousePress(bar, Qt.MouseButton.LeftButton, pos=QPoint(100, 20))
        QTest.mouseMove(bar, QPoint(150, 70))
        QTest.mouseRelease(bar, Qt.MouseButton.LeftButton, pos=QPoint(150, 70))
        self.assertNotEqual(window.pos(), original)
        self.assertTrue(desktop.manager.rect().contains(window.geometry()))
        controls = {b.accessibleName(): b for b in bar.findChildren(QPushButton)}
        controls['Minimize'].click()
        self.assertTrue(window.minimized)
        self.assertTrue(window.isHidden())
        desktop.task_buttons['terminal'].click()
        self.assertFalse(window.minimized)
        self.assertFalse(window.isHidden())
        before = window.geometry()
        controls['Maximize / Restore'].click()
        self.assertEqual(window.geometry(), desktop.manager.rect())
        controls['Maximize / Restore'].click()
        self.assertEqual(window.geometry(), before)
        controls['Close'].click()
        self.assertNotIn('terminal', desktop.manager.windows)
        self.assertNotIn('terminal', desktop.task_buttons)

    def test_bounds_and_foreground_click(self):
        desktop = self.desktop()
        terminal = desktop.manager.windows['terminal']
        system = desktop.open_app('system')
        terminal.move_bounded(QPoint(-10000, -10000))
        self.assertEqual(terminal.pos(), QPoint(0, 0))
        terminal.move_bounded(QPoint(10000, 10000))
        self.assertTrue(desktop.manager.rect().contains(terminal.geometry()))
        self.assertEqual(desktop.manager.active_key, 'system')
        terminal.move_bounded(QPoint(100, 100))
        system.move_bounded(QPoint(400, 180))
        def owner_at(point):
            widget = desktop.manager.childAt(point)
            while widget is not None and widget not in desktop.manager.windows.values():
                widget = widget.parentWidget()
            return widget
        self.assertIs(owner_at(QPoint(450, 200)), system)
        QTest.mouseClick(terminal.content.output.viewport(), Qt.MouseButton.LeftButton)
        self.assertEqual(desktop.manager.active_key, 'terminal')
        self.assertIs(owner_at(QPoint(450, 200)), terminal)
        self.window.resize(800, 500)
        self.app.processEvents()
        self.assertTrue(desktop.manager.rect().contains(terminal.geometry()))
        self.assertTrue(desktop.manager.rect().contains(system.geometry()))

    def test_long_terminal_history_stays_inside_small_desktop(self):
        desktop = self.desktop()
        window = desktop.manager.windows['terminal']
        window.content.output.appendPlainText('\n'.join(f'line {i}' for i in range(200)))
        self.app.processEvents()
        self.window.resize(800, 500)
        self.app.processEvents()
        self.assertTrue(desktop.manager.rect().contains(window.geometry()))
        window.toggle_maximize()
        self.assertEqual(window.geometry(), desktop.manager.rect())

    def test_automatic_transition_and_audio_warning(self):
        self.login()
        self.window.transition.start(1)
        deadline = time.monotonic() + 1
        while self.window.desktop is None and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.01)
        self.assertIsNotNone(self.window.desktop)
        self.window.audio_warning('Ses aygıtı kullanılamıyor')
        self.assertIn('Ses uyarısı', self.window.desktop.subtitle.text())

    def test_missing_audio_warns_without_blocking(self):
        warnings = []
        self.window.sound.warning.connect(warnings.append)
        self.real_sound_play(self.window.sound)
        self.assertTrue(warnings)
        self.assertIn('sessiz', self.window.audio_message)

    def test_sound_decode_error_is_nonfatal(self):
        from PySide6.QtMultimedia import QSoundEffect
        warnings = []
        self.window.sound.warning.connect(warnings.append)
        self.window.sound.requested = True
        with patch.object(self.window.sound.effect, 'status', return_value=QSoundEffect.Status.Error):
            self.window.sound._status_changed()
        self.assertTrue(warnings)
        self.assertFalse(self.window.sound.requested)

    def test_desktop_failure_retries_same_core(self):
        self.login()
        core = self.window.core
        with patch('akm.gui.app.Desktop', side_effect=ValueError('missing resource')):
            self.window.open_desktop()
        self.assertIsNone(self.window.desktop)
        self.assertIn('Desktop açılamadı', self.window.login_page.error.text())
        self.window.open_desktop()
        self.assertIs(self.window.desktop.core, core)

    def test_unstarted_core_rejected(self):
        from akm import AKMCore
        with self.assertRaises(ValueError):
            Desktop(AKMCore(self.root))
