"""Small synchronous event bus. It does not communicate between processes."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from itertools import count
from types import MappingProxyType


@dataclass(frozen=True)
class Event:
    topic: str
    payload: Mapping[str, object]


Listener = Callable[[Event], None]


class EventService:
    def __init__(self) -> None:
        self._listeners: dict[str, dict[int, Listener]] = {}
        self._tokens = count()

    def subscribe(self, topic: str, listener: Listener) -> Callable[[], None]:
        """Return an idempotent unsubscribe function for this registration."""
        if not topic or not callable(listener):
            raise ValueError('An event topic and callable listener are required.')
        token = next(self._tokens)
        self._listeners.setdefault(topic, {})[token] = listener

        def unsubscribe() -> None:
            listeners = self._listeners.get(topic, {})
            listeners.pop(token, None)
            if not listeners:
                self._listeners.pop(topic, None)

        return unsubscribe

    def unsubscribe(self, topic: str, listener: Listener) -> None:
        """Remove all registrations of a listener on a topic."""
        listeners = self._listeners.get(topic, {})
        for token, registered in tuple(listeners.items()):
            if registered == listener:
                del listeners[token]
        if not listeners:
            self._listeners.pop(topic, None)

    def emit(self, topic: str, **payload: object) -> tuple[Exception, ...]:
        """Dispatch a snapshot in order; a failed observer cannot undo an operation.

        The returned exceptions let callers diagnose observer failures. Payload
        keys are read-only; mutable values should not be modified by observers.
        Subscribe/unsubscribe during dispatch takes effect on the next emission.
        """
        event = Event(topic, MappingProxyType(dict(payload)))
        failures = []
        for listener in tuple(self._listeners.get(topic, {}).values()):
            try:
                listener(event)
            except Exception as exc:
                failures.append(exc)
        return tuple(failures)
