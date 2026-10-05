"""Composition root for the shared AKM services."""

from pathlib import Path

from .services.events import EventService
from .services.settings import SettingsService


class AKMCore:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.events = EventService()
        self.settings = SettingsService(self.root / 'Data' / 'settings.json', self.events)
