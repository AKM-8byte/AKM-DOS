import unittest
from pathlib import Path

from akm import AKMCore
from akm.services.events import EventService


class EventServiceTests(unittest.TestCase):
    def test_independent_cores_and_topics(self):
        first, second = AKMCore(Path.cwd()), AKMCore(Path.cwd())
        received = []
        first.events.subscribe('filesystem.changed', received.append)
        second.events.emit('filesystem.changed', operation='mkdir')
        first.events.emit('settings.changed', key='theme')
        self.assertEqual(received, [])
        first.events.emit('filesystem.changed', operation='mkdir', path='Games')
        self.assertEqual(received[0].payload['path'], 'Games')
        with self.assertRaises(TypeError):
            received[0].payload['path'] = 'modified'

    def test_unsubscribe_registration_and_listener(self):
        events = EventService()
        received = []
        stop = events.subscribe('change', received.append)
        events.subscribe('change', received.append)
        stop()
        stop()
        events.emit('change')
        self.assertEqual(len(received), 1)
        events.unsubscribe('change', received.append)
        events.emit('change')
        self.assertEqual(len(received), 1)

    def test_failed_observer_does_not_stop_other_observers(self):
        events = EventService()
        received = []

        def failing(event):
            raise RuntimeError('observer failed')

        events.subscribe('change', failing)
        events.subscribe('change', received.append)
        failures = events.emit('change')
        self.assertEqual(len(received), 1)
        self.assertEqual(len(failures), 1)
        self.assertIsInstance(failures[0], RuntimeError)

    def test_subscription_changes_use_dispatch_snapshot(self):
        events = EventService()
        received = []
        stop = events.subscribe('change', lambda event: received.append('original'))

        def update(event):
            stop()
            events.subscribe('change', lambda event: received.append('new'))

        events.subscribe('change', update)
        events.emit('change')
        self.assertEqual(received, ['original'])
        events.emit('change')
        self.assertEqual(received, ['original', 'new'])
