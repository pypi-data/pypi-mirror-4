confduino is an arduino_ library configurator

Links:
 * home: https://github.com/ponty/confduino
 * documentation: http://ponty.github.com/confduino
 
Features:
 - list, install, remove arduino_ libraries
    - install libraries from internet or local drive
    - fix ``examples`` directory name before installing
    - clean library (.*,_*,..) before installing
    - move examples under ``examples`` directory
    - upgrade library to 1.0: replace ``#include "wprogram.h"`` with ``#include "Arduino.h"``
 - list, install, remove arduino_ programmers
 - list, install, remove arduino_ boards
 - written in python
 - cross-platform
 - can be used as a python library or as a console program
 - unpacker back-end: pyunpack_
 - downloader back-end: urllib_
 - some functionality is based on arscons_
 - supported python versions: 2.6, 2.7
 - supported Arduino versions: 0022, 0023, 1.0, 1.0.3
 
Known problems:
 - tested only on linux
 - some libraries with unusual structure can not be installed
 - not all commands have console interface

arduino libraries: http://www.arduino.cc/en/Reference/Libraries
 
Basic usage
============

install library:

    >>> from confduino.libinstall import install_lib
    >>> install_lib('http://arduino.cc/playground/uploads/Main/PS2Keyboard002.zip')

or on console::

    python -m confduino.libinstall http://arduino.cc/playground/uploads/Main/PS2Keyboard002.zip

install a lot of libraries::

    python -m confduino.libinstall.examples.upgrademany

Installation
============

General
--------

 * install arduino_
 * install python_
 * install pip_
 * install back-ends for pyunpack_ (optional)
 * install the program::

    # as root
    pip install confduino
    


Ubuntu
----------
::

    sudo apt-get install arduino
    sudo apt-get install python-pip
    sudo pip install confduino
    sudo apt-get install unzip unrar p7zip-full

Uninstall
----------

::

    # as root
    pip uninstall confduino


.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _pip: http://pip.openplans.org/
.. _arduino: http://arduino.cc/
.. _python: http://www.python.org/
.. _urllib: http://docs.python.org/library/urllib.html
.. _arscons: http://code.google.com/p/arscons/
.. _pyunpack: https://github.com/ponty/pyunpack
