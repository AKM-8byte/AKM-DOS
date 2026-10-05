"""Regression tests for the existing 0.6 shell; no host applications are started."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class ShellRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for name, value in {
            'ROOT': self.root,
            'USERS_DIR': self.root / 'Users',
            'LEGACY_USER_FILE': self.root / 'Kullanıcı' / 'kullanıcı_ad.txt',
        }.items():
            p = patch.object(main, name, value)
            p.start()
            self.addCleanup(p.stop)
        with patch('builtins.input', return_value='Test User'), contextlib.redirect_stdout(io.StringIO()):
            self.shell = main.AKMShell()

    def capture(self, callback, argument=''):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            callback(argument)
        return output.getvalue()

    def test_home_and_legacy_profile(self):
        for folder in ('Desktop', 'Documents', 'Downloads', 'Settings'):
            self.assertTrue((self.shell.home / folder).is_dir())
        self.assertEqual((self.shell.home / 'Settings' / 'profile.txt').read_text(encoding='utf-8'), 'username=Test User\n')
        main.LEGACY_USER_FILE.parent.mkdir()
        main.LEGACY_USER_FILE.write_text('Eski Kullanıcı', encoding='utf-8')
        with patch('builtins.input', side_effect=AssertionError('unexpected input')):
            self.assertEqual(main.AKMShell().username, 'Eski Kullanıcı')

    def test_file_commands_and_home_protection(self):
        self.capture(self.shell.cmd_mkdir, 'Games')
        self.capture(self.shell.cmd_cd, 'Games')
        self.capture(self.shell.cmd_touch, 'test.txt')
        target = self.shell.cwd / 'test.txt'
        target.write_text('Türkçe içerik', encoding='utf-8')
        self.assertIn('Türkçe içerik', self.capture(self.shell.cmd_type, 'test.txt'))
        self.assertIn('test.txt', self.capture(self.shell.cmd_dir))
        self.capture(self.shell.cmd_delete, 'test.txt')
        self.assertFalse(target.exists())
        self.capture(self.shell.cmd_cd, '~')
        self.capture(self.shell.cmd_delete, 'Games')
        self.capture(self.shell.cmd_delete, '~')
        self.assertTrue(self.shell.home.exists())
        self.assertFalse((self.shell.home / 'Games').exists())

    def test_touch_keeps_existing_contents_and_delete_keeps_nonempty_directory(self):
        target = self.shell.home / 'keep.txt'
        target.write_text('keep', encoding='utf-8')
        self.capture(self.shell.cmd_touch, 'keep.txt')
        self.assertEqual(target.read_text(), 'keep')
        self.capture(self.shell.cmd_mkdir, 'Full')
        (self.shell.home / 'Full' / 'keep.txt').write_text('keep')
        with self.assertRaises(OSError):
            self.capture(self.shell.cmd_delete, 'Full')

    def test_aliases_and_long_session(self):
        for alias, canonical in [('help', 'yardım'), ('ls', 'dir'), ('cat', 'type'), ('del', 'sil'), ('exit', 'kapat')]:
            self.assertEqual(self.shell.commands[alias], self.shell.commands[canonical])
        with patch('builtins.input', side_effect=['help'] * 1100 + ['exit']), contextlib.redirect_stdout(io.StringIO()):
            self.shell.run()
        self.assertFalse(self.shell.running)

    def test_unknown_command_and_error_recovery(self):
        output = io.StringIO()
        with patch('builtins.input', side_effect=['unknown', 'mkdir Games', 'mkdir Games', 'version', 'exit']), contextlib.redirect_stdout(output):
            self.shell.run()
        self.assertIn('Bilinmeyen komut', output.getvalue())
        self.assertIn('Hata:', output.getvalue())
        self.assertIn(main.VERSION, output.getvalue())

    def test_calculator_and_system_info(self):
        with patch('builtins.input', side_effect=['5', '*', '3']):
            self.assertIn('15.0', self.capture(self.shell.cmd_calc))
        with patch('builtins.input', side_effect=['5', '/', '0']):
            self.assertIn('Hesaplama hatası', self.capture(self.shell.cmd_calc))
        self.assertIn('Python', self.capture(self.shell.cmd_systeminfo))

    def test_python_app_launches_use_current_interpreter(self):
        import sys
        (self.root / 'Programs').mkdir()
        for name in ('aka.py', 'Programs/notepad.py', 'Programs/webbrowser.py'):
            (self.root / name).touch()
        with patch('subprocess.Popen') as launch:
            self.shell.cmd_explorer('')
            self.shell.cmd_browser('')
            self.shell.cmd_notepad('')
        self.assertEqual(launch.call_count, 3)
        for call in launch.call_args_list:
            self.assertEqual(call.args[0][0], sys.executable)
            self.assertEqual(call.kwargs['cwd'], str(self.root))


if __name__ == '__main__':
    unittest.main()
