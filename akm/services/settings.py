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

    def set(self, key: str, value: object) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValueError('A nonempty settings key is required.')
        # JSON roundtrip validates input and removes references to caller data.
        encoded_value = json.dumps(value, ensure_ascii=False, allow_nan=False)
        value = json.loads(encoded_value)
        if key in self._values and self._values[key] == value:
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
