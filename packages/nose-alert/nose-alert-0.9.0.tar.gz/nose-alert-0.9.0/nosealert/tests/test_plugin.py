import unittest
from mock import Mock
from nosealert.plugin import AlertPlugin
from nosealert.notifications import Notification


class TestAlertPlugin(unittest.TestCase):

    def setUp(self):
        self.plugin = AlertPlugin()

    def test_get_notification_success(self):
        result = Mock(
            failures=[],
            errors=[],
            testsRun=3,
        )

        self.assertEqual(self.plugin.get_notification(result), Notification(
            total=3,
        ))

    def test_get_notification_with_fails(self):
        result = Mock(
            failures=[1, 2],
            errors=[3],
            testsRun=5,
        )

        self.assertEqual(self.plugin.get_notification(result), Notification(
            fails=2,
            errors=1,
            total=5,
        ))

    def test_finalize_sends_notification(self):
        notification = Mock()
        result = Mock()
        self.plugin.get_notification = Mock(return_value=notification)
        self.plugin.finalize(result)
        notification.send.assert_called_once_with()

