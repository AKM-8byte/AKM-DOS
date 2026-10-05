"""AKM logical paths backed by existing user/program folders.

Host paths and drive bridges are readable; writes are limited to AKM user and
program folders in this foundation. This API boundary is not a Python sandbox.
"""

from dataclasses import dataclass
from pathlib import Path

from .events import EventService


@dataclass(frozen=True)
class FileEntry:
    name: str
    path: Path
    is_directory: bool


class FileSystemService:
    def __init__(self, root: Path, home: Path, events: EventService,
                 drives: dict[str, Path] | None = None) -> None:
        self.root = Path(root).resolve()
        self.home = Path(home).absolute()
        self.managed_root = self.root / 'Data'
        self.system = self.managed_root / 'System'
        self.programs = self.root / 'Programs'
        self.drive_directory = self.managed_root / 'Drives'
        self.events = events
        self.drives = {name.upper(): Path(path).resolve() for name, path in (drives or {}).items()}

    def prepare_user(self, username: str) -> None:
        # Bootstrap must not follow a redirected Data, Users or Programs mount.
        for path in (self.home, self.managed_root, self.programs):
            if not path.resolve().is_relative_to(self.root):
                raise PermissionError(f'AKM mount leaves the application root: {path}')
        for path in (self.system, self.drive_directory, self.programs):
            if not path.resolve().is_relative_to(self.root):
                raise PermissionError(f'AKM mount leaves the application root: {path}')
            path.mkdir(parents=True, exist_ok=True)
        for folder in ('Desktop', 'Documents', 'Downloads', 'Settings'):
            target = self.home / folder
            self._check_write(target.resolve())
            target.mkdir(parents=True, exist_ok=True)
        profile = self.home / 'Settings' / 'profile.txt'
        self._check_write(profile.resolve())
        if not profile.exists():
            profile.write_text(f'username={username}\n', encoding='utf-8')

    @staticmethod
    def _beneath(base: Path, parts: list[str]) -> Path:
        # A colon in the tail could be an absolute Windows path or NTFS stream.
        if any(':' in part for part in parts):
            raise ValueError('Invalid AKM path component.')
        target = base.joinpath(*parts).resolve()
        if not target.is_relative_to(base.absolute()):
            raise PermissionError('AKM path leaves its mapped folder.')
        return target

    def resolve(self, value: str | Path = '', cwd: Path | None = None) -> Path:
        raw = str(value).strip()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
            raw = raw[1:-1]
        if not raw or raw == '~':
            return self.home.resolve()
        normalized = raw.replace('\\', '/')
        if normalized.startswith('~/'):
            return self._beneath(self.home, normalized[2:].split('/'))
        if normalized[:5].upper() == 'AKM:/':
            parts: list[str] = []
            for part in normalized[5:].split('/'):
                if part in ('', '.'):
                    continue
                if part == '..':
                    if not parts:
                        raise PermissionError('AKM path leaves the logical root.')
                    parts.pop()
                else:
                    parts.append(part)
            if not parts:
                return self.managed_root
            mount = parts.pop(0).lower()
            if mount == 'drives':
                if not parts:
                    return self.drive_directory
                name = parts.pop(0).upper()
                if name not in self.drives:
                    raise FileNotFoundError(f'Drive not found: {name}')
                return self._beneath(self.drives[name], parts)
            mounts = {'user': self.home, 'system': self.system, 'programs': self.programs}
            if mount not in mounts:
                raise FileNotFoundError(f'AKM folder not found: {mount}')
            return self._beneath(mounts[mount], parts)
        path = Path(raw)
        return path.resolve() if path.is_absolute() else ((cwd or self.home) / path).resolve()

    def list_directory(self, value: str | Path = '', cwd: Path | None = None) -> list[FileEntry]:
        target = self.resolve(value, cwd) if value else (cwd or self.home)
        if target == self.managed_root:
            entries = [FileEntry('System', self.system, True), FileEntry('Programs', self.programs, True),
                       FileEntry('User', self.home, True), FileEntry('Drives', self.drive_directory, True)]
        elif target == self.drive_directory:
            entries = [FileEntry(name, path, True) for name, path in self.drives.items()]
        else:
            entries = [FileEntry(path.name, path, path.is_dir()) for path in target.iterdir()]
        return sorted(entries, key=lambda item: (not item.is_directory, item.name.lower()))

    def _check_write(self, target: Path) -> None:
        if target.is_relative_to(self.system.resolve()):
            raise PermissionError('AKM:/System normal kullanımda korunur.')
        if not any(target.is_relative_to(base) for base in (self.home, self.programs)):
            raise PermissionError('Bu aşamada yalnızca AKM User ve Programs alanına yazılabilir; gerçek diskler salt okunur.')
        if target == self.home or target == self.programs:
            raise PermissionError('AKM mount root cannot be modified.')
        if ':' in target.name:
            raise ValueError('NTFS alternate streams are not supported.')

    def mkdir(self, value: str | Path, cwd: Path | None = None) -> Path:
        target = self.resolve(value, cwd)
        self._check_write(target)
        target.mkdir(parents=True, exist_ok=False)
        self.events.emit('filesystem.changed', operation='mkdir', path=str(target))
        return target

    def touch(self, value: str | Path, cwd: Path | None = None) -> Path:
        target = self.resolve(value, cwd)
        self._check_write(target)
        if target.is_dir():
            raise IsADirectoryError(str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch(exist_ok=True)
        self.events.emit('filesystem.changed', operation='touch', path=str(target))
        return target

    def read_text(self, value: str | Path, cwd: Path | None = None) -> str:
        return self.resolve(value, cwd).read_text(encoding='utf-8')

    def delete(self, value: str | Path, cwd: Path | None = None) -> str | None:
        target = self.resolve(value, cwd)
        self._check_write(target)
        if target.is_file():
            target.unlink()
            kind = 'file'
        elif target.is_dir():
            target.rmdir()
            kind = 'directory'
        else:
            return None
        self.events.emit('filesystem.changed', operation='delete', path=str(target))
        return kind
