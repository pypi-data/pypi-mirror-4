try:
    from widgets import FullScreenTextarea
except ImportError:
    pass

version = (1, 0, 7)


def get_version():
    """returns a pep complient version number"""
    return '.'.join(str(i) for i in version)
