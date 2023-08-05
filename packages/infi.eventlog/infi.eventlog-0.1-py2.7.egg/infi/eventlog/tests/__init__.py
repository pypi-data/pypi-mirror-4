from unittest import SkipTest
from infi import unittest
from infi.eventlog import LocalEventLog

class FacadeTestCase(unittest.TestCase):
    def test__open_system_channel(self):
        eventlog = LocalEventLog()
        with eventlog.open_channel_context("System"):
            pass

    def test__get_available_channels(self):
        eventlog = LocalEventLog()
        channels = list(eventlog.get_available_channels())
        self.assertIn("System", channels)

    def test_get_query_generator(self):
        eventlog = LocalEventLog()
        list(eventlog.event_query("System"))