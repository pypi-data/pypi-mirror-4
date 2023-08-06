"""
A nose plugin showing success/failure status notification.
"""


VERSION = (0, 9, 0)

__version__ = '.'.join((str(each) for each in VERSION[:4]))

def get_version():
    """
    Returns shorter version (digit parts only) as string.
    """
    return '.'.join((str(each) for each in VERSION[:4]))

