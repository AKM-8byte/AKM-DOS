import tempfile
import unittest
from pathlib import Path

from akm.services.events import EventService
from akm.services.filesystem import FileSystemService


class FileSystemServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.host = self.root / 'host-drive'
        self.host.mkdir()
        self.events = EventService()
        self.received = []
        self.events.subscribe('filesystem.changed', self.received.append)
        self.fs = FileSystemService(self.root, self.root / 'Users' / 'Test', self.events, {'T:': self.host})
        self.fs.prepare_user('Test')

    def test_virtual_mounts_and_relative_paths(self):
        names = {entry.name for entry in self.fs.list_directory('AKM:/')}
        self.assertEqual(names, {'System', 'Programs', 'User', 'Drives'})
        self.assertEqual(self.fs.resolve('AKM:/User/Documents'), self.fs.home / 'Documents')
        self.assertEqual(self.fs.resolve('akm:\\User\\Documents'), self.fs.home / 'Documents')
        self.assertEqual(self.fs.resolve('~/Documents'), self.fs.home / 'Documents')
        self.assertEqual(self.fs.resolve('"Documents"'), self.fs.home / 'Documents')
        self.assertEqual(self.fs.resolve('AKM:/User/../System'), self.fs.system)
        self.assertEqual([entry.name for entry in self.fs.list_directory('AKM:/Drives')], ['T:'])
        with self.assertRaises(FileNotFoundError):
            self.fs.resolve('AKM:/Missing')
        with self.assertRaises(PermissionError):
            self.fs.resolve('AKM:/../../outside')

    def test_successful_mutations_notify_but_failed_operations_do_not(self):
        self.fs.mkdir('Games')
        file = self.fs.touch('Games/save.txt')
        file.write_text('Türkçe', encoding='utf-8')
        self.assertEqual(self.fs.read_text('Games/save.txt'), 'Türkçe')
        self.assertEqual(self.fs.delete('Games/save.txt'), 'file')
        self.assertEqual(self.fs.delete('Games'), 'directory')
        self.assertEqual([event.payload['operation'] for event in self.received], ['mkdir', 'touch', 'delete', 'delete'])
        self.assertIsNone(self.fs.delete('missing.txt'))
        self.fs.mkdir('Full')
        self.fs.touch('Full/keep.txt')
        before = len(self.received)
        with self.assertRaises(OSError):
            self.fs.delete('Full')
        self.assertEqual(len(self.received), before)

    def test_system_and_mount_roots_protected_through_all_path_forms(self):
        system_file = self.fs.system / 'keep.txt'
        system_file.write_text('keep')
        for value in ('AKM:/System/keep.txt', str(system_file), '../../Data/System/keep.txt'):
            for operation in (self.fs.touch, self.fs.delete):
                with self.assertRaises(PermissionError):
                    operation(value)
        for value in ('~', 'AKM:/', 'AKM:/Programs', 'AKM:/System', 'AKM:/Drives'):
            with self.assertRaises(PermissionError):
                self.fs.delete(value)
        self.assertEqual(system_file.read_text(), 'keep')
        self.assertEqual(self.received, [])

    def test_host_bridge_is_read_only_and_traversal_cannot_enable_writes(self):
        file = self.host / 'keep.txt'
        file.write_text('host contents')
        self.assertEqual(self.fs.read_text('AKM:/Drives/T:/keep.txt'), 'host contents')
        self.assertEqual(self.fs.read_text(str(file)), 'host contents')
        for value in ('AKM:/Drives/T:/keep.txt', str(file), '../../host-drive/keep.txt'):
            with self.assertRaises(PermissionError):
                self.fs.delete(value)
        with self.assertRaises(PermissionError):
            self.fs.touch('AKM:/Drives/T:/new.txt')
        self.assertEqual(file.read_text(), 'host contents')
        with self.assertRaises(ValueError):
            self.fs.touch('AKM:/User/file.txt:stream')

    def test_link_escape_is_rejected_without_changing_target(self):
        link = self.fs.home / 'host-link'
        try:
            link.symlink_to(self.host, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f'Symlink unavailable: {exc}')
        with self.assertRaises(PermissionError):
            self.fs.touch('host-link/new.txt')
        with self.assertRaises(PermissionError):
            self.fs.resolve('AKM:/User/host-link/new.txt')
        self.assertFalse((self.host / 'new.txt').exists())

    def test_bootstrap_rejects_redirected_user_folders(self):
        outside = self.root / 'elsewhere'
        outside.mkdir()
        # A redirected Settings directory must not receive bootstrap writes.
        settings = self.fs.home / 'Settings'
        (settings / 'profile.txt').unlink()
        settings.rmdir()
        try:
            settings.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f'Symlink unavailable: {exc}')
        with self.assertRaises(PermissionError):
            self.fs.prepare_user('Test')
        self.assertFalse((outside / 'profile.txt').exists())
