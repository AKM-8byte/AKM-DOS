import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from akm import AKMCore


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.core = AKMCore(self.root)

    def test_start_shares_events_and_preserves_existing_user_data(self):
        documents = self.root / 'Users' / 'User' / 'Documents'
        documents.mkdir(parents=True)
        (documents / 'keep.txt').write_text('keep')
        received = []
        self.core.events.subscribe('core.started', received.append)
        self.core.start('User')
        self.assertTrue(self.core.started)
        self.assertTrue(all(status == 'ready' for status in self.core.service_status.values()))
        self.assertIs(self.core.filesystem.events, self.core.events)
        self.assertIs(self.core.settings.events, self.core.events)
        self.assertEqual((documents / 'keep.txt').read_text(), 'keep')
        self.assertEqual(AKMCore(self.root).settings.get('user.name'), 'User')
        self.assertEqual(len(received), 1)
        with self.assertRaises(RuntimeError):
            self.core.start('User')

    def test_failed_service_does_not_report_started(self):
        received = []
        failures = []
        self.core.events.subscribe('core.started', received.append)
        self.core.events.subscribe('core.start_failed', failures.append)
        with patch.object(self.core.settings, 'set', side_effect=PermissionError('read-only settings')):
            with self.assertRaises(PermissionError):
                self.core.start('User')
        self.assertFalse(self.core.started)
        self.assertIsNone(self.core.filesystem)
        self.assertEqual(self.core.service_status['settings'], 'failed')
        self.assertEqual(failures[0].payload['service'], 'settings')
        self.assertEqual(received, [])

    def test_invalid_username_cannot_escape_user_folder(self):
        with self.assertRaises(ValueError):
            self.core.start('../outside')
        self.assertFalse(self.core.started)
