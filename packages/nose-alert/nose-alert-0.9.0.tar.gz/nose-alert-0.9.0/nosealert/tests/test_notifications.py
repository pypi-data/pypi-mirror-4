import unittest
from mock import Mock
from nosealert.notifications import IMAGES_DIR
from nosealert.notifications import get_icon
from nosealert.notifications import Notification
from os import path


class TestNotification(unittest.TestCase):

    def test_get_message(self):
        notification = Notification(total=11)
        self.assertEqual(notification.get_message(), 'All 11 tests passed.')

    def test_get_message_fails(self):
        notification = Notification(total=11, fails=3)
        self.assertEqual(notification.get_message(), '3 out of 11 tests failed!')

    def test_get_message_errors(self):
        notification = Notification(total=7, errors=5)
        self.assertEqual(notification.get_message(), '5 out of 7 tests failed!')

    def test_get_message_fails_and_errors(self):
        notification = Notification(total=201, fails=1, errors=3)
        self.assertEqual(notification.get_message(), '4 out of 201 tests failed!')

    def test_get_title(self):
        notification = Notification(total=13)
        self.assertEqual(notification.get_title(), 'Success')

    def test_get_title_fails(self):
        notification = Notification(fails=2, total=13)
        self.assertEqual(notification.get_title(), 'Failed')

    def test_get_title_errors(self):
        notification = Notification(errors=2, total=13)
        self.assertEqual(notification.get_title(), 'Failed')

    def test_get_title_fails_and_fails(self):
        notification = Notification(fails=2, errors=5, total=20)
        self.assertEqual(notification.get_title(), 'Failed')

    def test_send_calls_notify_with_proper_args(self):
        notification = Notification('My App')
        notification.get_title = Mock(return_value='foo')
        notification.get_message = Mock(return_value='bar')
        notification.notify = Mock()
        notification.send()
        notification.notify.assert_called_once_with(
            sender='My App',
            title='foo',
            message='bar',
            success=True,
        )
    def test_send_calls_notify_with_proper_args_on_fails(self):
        notification = Notification('My App', fails=1)
        notification.get_title = Mock(return_value='foo')
        notification.get_message = Mock(return_value='bar')
        notification.notify = Mock()
        notification.send()
        notification.notify.assert_called_once_with(
            sender='My App',
            title='foo',
            message='bar',
            success=False,
        )


class TestGetIcon(unittest.TestCase):

    def test_get_icon_on_success(self):
        self.assertTrue(get_icon(True) ==
            open(path.join(IMAGES_DIR, 'dialog-ok.png'), 'rb').read())

    def test_get_icon_on_error(self):
        self.assertTrue(get_icon(False) ==
            open(path.join(IMAGES_DIR, 'dialog-error.png'), 'rb').read())

