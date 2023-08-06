"""
"""
from nose.plugins import Plugin
from .notifications import Notification
from gntp.notifier import mini as growl


def notify(program_name, title, message):
    growl(message, program_name, title=title)


class AlertPlugin(Plugin):
    """
    Plugin that should fire os level notification after tests are finished.
    """
    name = 'alert'

    def get_notification(self, result):
        """
        Returns ``Notification`` instance for given nosetest ``result``.
        :param result: nosetest result that is passed to ``Plugin.finalize``
          method at the end of tests
        """
        return Notification(
            fails=len(result.failures),
            errors=len(result.errors),
            total=result.testsRun,
    )

    def finalize(self, result):
        """
        Shows notification about success or failure.
        """
        notification = self.get_notification(result)
        notification.send()


class WatchPlugin(Plugin):
    """
    Plugin that use watchdog for continuos tests run.
    """
    name = 'watch'
    is_watching = False

    def finalize(self, result):
        import sys
        from subprocess import call
        argv = list(sys.argv)
        argv.remove('--with-watch')
        watchcmd = 'clear && ' + ' '.join(argv)
        call(['watchmedo', 'shell-command', '-c', watchcmd, '-R', '-p', '*.py', '.'])

