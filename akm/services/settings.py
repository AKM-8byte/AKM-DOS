"""Single-user JSON settings with atomic replacement and change events."""

import copy
import json
import os
import tempfile
from pathlib import Path

from .events import EventService


class SettingsError(ValueError):
    """Invalid settings are reported without replacing the original file."""


class SettingsService:
    def __init__(self, path: Path, events: EventService) -> None:
        self.path = Path(path)
        self.events = events
        self._values: dict[str, object] = {}
        if self.path.exists():
            try:
                values = json.loads(self.path.read_text(encoding='utf-8'))
                if not isinstance(values, dict):
                    raise ValueError('The settings root must be a JSON object.')
                # Reject non-standard JSON values such as NaN before any write.
                json.dumps(values, allow_nan=False)
            except (ValueError, UnicodeError) as exc:
                raise SettingsError(f'Invalid settings file: {self.path}: {exc}') from exc
            self._values = values

    def get(self, key: str, default: object = None) -> object:
        return copy.deepcopy(self._values.get(key, default))

    def all(self) -> dict[str, object]:
        return copy.deepcopy(self._values)

    @staticmethod
    def legacy_username(path: Path) -> str | None:
        """Read the old username without changing or deleting legacy data."""
        if path.exists():
            return path.read_text(encoding='utf-8').strip() or None
        return None

    @staticmethod
    def profile_username(users_dir: Path) -> str | None:
        """Adopt a lone 0.6 profile; ambiguous old folders remain untouched."""
        if not users_dir.is_dir():
            return None
        candidates = []
        for folder in users_dir.iterdir():
            profile = folder / 'Settings' / 'profile.txt'
            if folder.is_dir() and profile.is_file():
                content = profile.read_text(encoding='utf-8').strip()
                name = content.removeprefix('username=')
                if content.startswith('username=') and name == folder.name:
                    candidates.append(name)
        return candidates[0] if len(candidates) == 1 else None

    def set(self, key: str, value: object) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValueError('A nonempty settings key is required.')
        # JSON roundtrip validates input and removes references to caller data.
        encoded_value = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)
        value = json.loads(encoded_value)
        if key in self._values and json.dumps(self._values[key], ensure_ascii=False, sort_keys=True) == encoded_value:
            return
        values = {**self._values, key: value}
        content = json.dumps(values, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        self._save(content)
        self._values = values
        self.events.emit('settings.changed', key=key, value=copy.deepcopy(value))

    def _save(self, content: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent,
                                             prefix='.settings-', suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
