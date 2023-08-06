VERSION = (0, 0, 5)

import hashlib


def get_version():
    if len(VERSION) > 3 and VERSION[3] != 'final':
        return '%s.%s.%s %s' % (VERSION[0], VERSION[1], VERSION[2], VERSION[3])
    else:
        return '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])

__version__ = get_version()


def hash_text(text):
    """
    Create a md5 hash for for a message string

    @param text:
    @rtype: str
    """
    encoding = text.encode("UTF-16LE")
    md5 = hashlib.md5()
    md5.update(encoding)
    return md5.hexdigest()

