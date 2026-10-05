"""Composition root for the shared AKM services."""

from pathlib import Path

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
        self.service_status['filesystem'] = 'ready'
        self.started = True
        self.events.emit('core.started', username=username, services=dict(self.service_status))
