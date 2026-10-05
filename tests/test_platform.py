import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from akm.platform.windows import WindowsBackend
from akm.services.platform import PlatformService


class PlatformServiceTests(unittest.TestCase):
    def test_color_rejects_shell_metacharacters(self):
        backend = WindowsBackend()
        with patch('akm.platform.windows.os.system') as command:
            for value in ('0A & echo bad', '0A|echo bad', 'ZZ', '', '000', '0A\n'):
                with self.assertRaises(ValueError):
                    backend.set_console_color(value)
            command.assert_not_called()
            backend.set_console_color('0A')
            command.assert_called_once_with('color 0A')

    def test_windows_backend_launches_device_manager_without_shell(self):
        with patch('akm.platform.windows.subprocess.Popen') as launch:
            WindowsBackend().open_device_manager()
        launch.assert_called_once_with(['mmc.exe', 'devmgmt.msc'], shell=False)

    def test_missing_backend_has_clear_error_and_portable_info(self):
        service = PlatformService(Path.cwd())
        service.backend = None
        self.assertEqual(service.discover_drives(), {})
        self.assertIn('python', service.system_info())
        with self.assertRaises(NotImplementedError):
            service.set_console_color('0A')

    def test_python_launch_cannot_escape_root(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            service = PlatformService(Path(temp))
            with patch('akm.services.platform.subprocess.Popen') as launch:
                with self.assertRaises(PermissionError):
                    service.launch_python('../escape.py')
                with self.assertRaises(FileNotFoundError):
                    service.launch_python('missing.py')
            launch.assert_not_called()
