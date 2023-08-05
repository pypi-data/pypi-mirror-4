from path import path
import logging
import os
import sys

__version__ = '0.2'

log = logging.getLogger(__name__)
# log=logging

log.debug('version=' + __version__)

_ARDUINO_PATH = None


def arduino_default_path():
    'platform specific default root path'
    if sys.platform == 'darwin':
        s = path('/Applications/Arduino.app/Contents/Resources/Java')
    elif sys.platform == 'win32':
        s = None
    else:
        s = path('/usr/share/arduino/')
    return s


def set_arduino_path(directory):
    global _ARDUINO_PATH
    _ARDUINO_PATH = directory


def arduino_path():
    'expanded root path, ARDUINO_HOME env var or arduino_default_path()'

    x = _ARDUINO_PATH
    if not x:
        x = os.environ.get('ARDUINO_HOME')

    if not x:
        x = arduino_default_path()

    assert x, str(x)

    x = path(x).expand().abspath()

    assert x.exists(), 'arduino path not found:' + str(x)
    return x
