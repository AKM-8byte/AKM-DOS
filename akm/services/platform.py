"""Portable runtime information and a narrow platform backend boundary."""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Protocol

from ..platform.windows import WindowsBackend


class PlatformBackend(Protocol):
    def clear_console(self) -> None: ...
    def set_console_color(self, code: str) -> None: ...
    def open_device_manager(self) -> None: ...
    def discover_drives(self) -> dict[str, Path]: ...


class PlatformService:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.backend: PlatformBackend | None = WindowsBackend() if os.name == 'nt' else None

    def system_info(self) -> dict[str, str]:
        return {'system': platform.system(), 'release': platform.release(),
                'machine': platform.machine(), 'python': platform.python_version()}

    def _require_backend(self) -> PlatformBackend:
        if self.backend is None:
            raise NotImplementedError('Bu işlem şu anda yalnızca Windows üzerinde destekleniyor.')
        return self.backend

    def clear_console(self) -> None:
        self._require_backend().clear_console()

    def set_console_color(self, code: str) -> None:
        self._require_backend().set_console_color(code)

    def open_device_manager(self) -> None:
        self._require_backend().open_device_manager()

    def discover_drives(self) -> dict[str, Path]:
        return self.backend.discover_drives() if self.backend is not None else {}

    def launch_python(self, relative_path: str | Path) -> subprocess.Popen:
        path = (self.root / relative_path).resolve()
        if not path.is_relative_to(self.root):
            raise PermissionError('Program yolu AKM-DOS klasörü dışında olamaz.')
        if not path.is_file():
            raise FileNotFoundError(f'Program bulunamadı: {relative_path}')
        return subprocess.Popen([sys.executable, str(path)], cwd=str(self.root))
