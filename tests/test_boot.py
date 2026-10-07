import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from akm.gui.boot import BootSession


class BootTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.boot = BootSession(self.root)

    def test_success_exposes_started_core_and_saved_user(self):
        core = self.boot.start('Ahmet')
        self.assertTrue(core.started)
        self.assertIs(self.boot.core, core)
        self.assertEqual(BootSession(self.root).start('Another').username, 'Ahmet')

    def test_legacy_user_precedes_fallback(self):
        legacy = self.root / 'Kullanıcı'
        legacy.mkdir()
        (legacy / 'kullanıcı_ad.txt').write_text('Eski Kullanıcı', encoding='utf-8')
        self.assertEqual(self.boot.start('New').username, 'Eski Kullanıcı')

    def test_broken_settings_preserved_and_no_desktop_core(self):
        data = self.root / 'Data'
        data.mkdir()
        settings = data / 'settings.json'
        settings.write_text('{broken', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.boot.start('User')
        self.assertIsNone(self.boot.core)
        self.assertTrue(self.boot.error)
        self.assertEqual(settings.read_text(), '{broken')

    def test_service_failure_then_explicit_retry(self):
        with patch('akm.services.settings.SettingsService.set', side_effect=PermissionError('read-only')):
            with self.assertRaises(PermissionError):
                self.boot.start('User')
        self.assertIsNone(self.boot.core)
        self.assertEqual(self.boot.service_status['settings'], 'failed')
        self.assertTrue(self.boot.start('User').started)

    def test_empty_user_cannot_start(self):
        with self.assertRaises(ValueError):
            self.boot.start('')
        self.assertIsNone(self.boot.core)

    def test_blank_saved_name_falls_back_like_shell(self):
        data = self.root / 'Data'
        data.mkdir()
        (data / 'settings.json').write_text('{"user.name": "   "}')
        self.assertEqual(self.boot.start('Ahmet').username, 'Ahmet')

    def test_post_does_not_create_user_until_login(self):
        prepared = self.boot.prepare()
        self.assertFalse(prepared.started)
        self.assertEqual(self.boot.service_status['filesystem'], 'not_started')
        self.assertFalse((self.root / 'Users').exists())
        self.assertIsNone(self.boot.core)
        self.assertIs(self.boot.login('Ahmet'), prepared)
        self.assertTrue(prepared.started)

    def test_login_requires_post(self):
        with self.assertRaises(RuntimeError):
            self.boot.login('User')
