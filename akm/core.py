"""Composition root for the shared AKM services."""

from pathlib import Path

from .services.events import EventService


class AKMCore:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.events = EventService()
