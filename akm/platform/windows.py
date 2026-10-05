"""Windows-only operations are kept out of the core and shell."""

import ctypes
import os
import re
import subprocess
from pathlib import Path


class WindowsBackend:
    def clear_console(self) -> None:
        os.system('cls')

    def set_console_color(self, code: str) -> None:
        if not re.fullmatch(r'[0-9a-fA-F]{1,2}', code):
            raise ValueError('Windows renk kodu 1 veya 2 hexadecimal karakter olmalı.')
        os.system(f'color {code}')

    def open_device_manager(self) -> None:
        subprocess.Popen(['mmc.exe', 'devmgmt.msc'], shell=False)

    def discover_drives(self) -> dict[str, Path]:
        mask = ctypes.windll.kernel32.GetLogicalDrives()
        return {f'{chr(65 + index)}:': Path(f'{chr(65 + index)}:/')
                for index in range(26) if mask & (1 << index)}
