import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from akm.services.events import EventService
from akm.services.settings import SettingsError, SettingsService


class SettingsServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'Settings' / 'settings.json'
        self.events = EventService()
        self.received = []
        self.events.subscribe('settings.changed', self.received.append)
        self.settings = SettingsService(self.path, self.events)

    def test_persist_unicode_and_emit_after_save(self):
        seen_on_disk = []
        self.events.subscribe('settings.changed', lambda event: seen_on_disk.append(json.loads(self.path.read_text(encoding='utf-8'))))
        self.settings.set('user.name', 'Türkçe Kullanıcı')
        self.assertEqual(SettingsService(self.path, self.events).get('user.name'), 'Türkçe Kullanıcı')
        self.assertEqual(seen_on_disk, [{'user.name': 'Türkçe Kullanıcı'}])
        self.assertEqual(self.received[0].payload['key'], 'user.name')
        self.settings.set('user.name', 'Türkçe Kullanıcı')
        self.assertEqual(len(self.received), 1)

    def test_missing_settings_and_mutable_value_isolation(self):
        self.assertFalse(self.path.exists())
        self.assertEqual(self.settings.get('theme', 'classic'), 'classic')
        value = {'colors': ['blue']}
        self.settings.set('theme', value)
        value['colors'].append('red')
        fetched = self.settings.get('theme')
        fetched['colors'].append('green')
        self.settings.all()['theme']['colors'].append('white')
        self.assertEqual(self.settings.get('theme'), {'colors': ['blue']})

    def test_invalid_files_are_not_overwritten(self):
        self.path.parent.mkdir()
        for text in ('{broken', '[]', '{"value": NaN}'):
            self.path.write_text(text, encoding='utf-8')
            with self.assertRaises(SettingsError):
                SettingsService(self.path, self.events)
            self.assertEqual(self.path.read_text(), text)

    def test_failed_replace_preserves_memory_disk_and_events(self):
        self.settings.set('theme', 'classic')
        original = self.path.read_text()
        self.received.clear()
        with patch('akm.services.settings.os.replace', side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                self.settings.set('theme', 'modern')
        self.assertEqual(self.path.read_text(), original)
        self.assertEqual(self.settings.get('theme'), 'classic')
        self.assertEqual(self.received, [])
        self.assertEqual(list(self.path.parent.glob('.settings-*.tmp')), [])

    def test_non_json_values_do_not_change_state(self):
        for value in (object(), float('nan')):
            with self.assertRaises((TypeError, ValueError)):
                self.settings.set('invalid', value)
        with self.assertRaises(ValueError):
            self.settings.set('', 'value')
        self.assertFalse(self.path.exists())
        self.assertEqual(self.settings.all(), {})
