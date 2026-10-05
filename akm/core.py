"""Composition root for the shared AKM services."""

from datetime import datetime, timezone
from pathlib import Path
import traceback

from .services.events import EventService
from .services.filesystem import FileSystemService
from .services.platform import PlatformService
from .services.settings import SettingsService


class AKMCore:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.events = EventService()
        if not (self.root / 'Data').resolve().is_relative_to(self.root):
            raise PermissionError('AKM Data folder leaves the application root.')
        self.settings = SettingsService(self.root / 'Data' / 'settings.json', self.events)
        self.platform = PlatformService(self.root)
        self.filesystem: FileSystemService | None = None
        self.service_status = {'events': 'ready', 'settings': 'ready',
                               'platform': 'ready', 'filesystem': 'not_started'}
        self.started = False
        self.username: str | None = None

    def start(self, username: str) -> None:
        """Initialize the selected single user; report actual startup outcomes."""
        if self.started:
            raise RuntimeError('AKMCore is already started.')
        if not username or any(character not in ' _-' and not character.isalnum() for character in username):
            raise ValueError('Invalid AKM username.')
        home = self.root / 'Users' / username
        service = 'platform'
        try:
            drives = self.platform.discover_drives()
            service = 'filesystem'
            filesystem = FileSystemService(self.root, home, self.events, drives)
            filesystem.prepare_user(username)
            service = 'settings'
            self.settings.set('user.name', username)
        except Exception as exc:
            self.service_status[service] = 'failed'
            self.events.emit('core.start_failed', service=service, error=str(exc))
            raise
        self.filesystem = filesystem
        for service in ('platform', 'filesystem', 'settings'):
            self.service_status[service] = 'ready'
        self.started = True
        self.username = username
        self.events.emit('core.started', username=username, services=dict(self.service_status))

    def log_error(self, exc: Exception) -> None:
        """Append a diagnostic without changing the legacy crash-screen file."""
        log_dir = self.root / 'Data' / 'logs'
        if not log_dir.resolve().is_relative_to(self.root / 'Data'):
            raise PermissionError('Log directory leaves the AKM data folder.')
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'shell.log'
        if not log_path.resolve().is_relative_to(log_dir):
            raise PermissionError('Log file leaves the AKM log folder.')
        timestamp = datetime.now(timezone.utc).isoformat()
        with log_path.open('a', encoding='utf-8') as stream:
            stream.write(f'[{timestamp}]\n')
            stream.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
