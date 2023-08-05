PYAHK AutoHotKey via Python
===========================
:Description: Python ctypes wrapper around AutoHotKey dll.
:License: BSD-style, see `LICENSES.txt`_
:Author: Ed Blake <kitsu.eb@gmail.com>
:Date: Sep. 19 2012
:Revision: 12

Introduction
------------
`AutoHotKey <http://www.autohotkey.com/>`_ is a powerful task automator with a
terrible scripting language built-in. Python is a powerful scripting language
with old, unmaintained, and incomplete automation modules. Combining the two
creates a powerful automation tool with a powerful scripting back-end with 
access to all the power of the Python standard library.

This is made possible by the amazing Python ctypes module and the
AutoHotKey.dll_ project. Together they allow exchange of data between both
scripting engines, and the execution of AHK commands from Python.

Requirements
------------
* Written for Python2.7_, not currently py3k compatible.
* Written against AutoHotkey_H ANSI 32-bit Version 1.1.8.1 (on WinXP).
* A copy of the ANSI 32-bit dll must be provided either in the system location
  of your version of Windows, or in the same folder as the ahk.py file.
  (The required dll is not provided as part of this distribution, see the
  AutoHotKey.dll_ site for download instructions.)

Installation
------------
Currently only: `python setup.py install`

Testing
-------
A helper script "runtests.py" is provided in the project root to run the entire 
test suite. Runnable test scripts are provided for each sub-module in the test 
folder. Tests require Michael Foord's `mock library`_.

Usage
-----
First import the ahk module::

    import ahk

Lower level function wrappers provide more direct access to the underlaying dll::

    ahk.start() # Ititializes a new script thread
    ahk.ready() # Waits until status is True
    ahk.execute('a := WinActive("Notepad")') # Sets a to the return value of WinActive
    print get('a') # prints the HWND of the found window or 0x0 as a string

Object wrappers are also provided which have a somewhat cleaner interface::

    script = ahk.Script() # Initializes with start and ready commands as above
    a = script.winActive("Notepad") # Sets a to the return value of the method
    print a # prints the HWND of the found window as an int, or None
    script.variable('b', float) # Creates a transparent variable attribute
    ahk.execute("Random, b, 0.0, 1.0") # Stores value in `b`
    print 100*script.b # b is retrieved and converted to its saved type (float)

See the Docs_ for further details.

ToDo
----
* Re-write script.Function to use the now working ahk.call function.
* Extend setup script with options to download/install the correct dll?
* Add remaining Control commands to Control class.
* Add doc-tests?
* Migrate docs to ReadTheDocs_? 
* Extend Script class with something to replace ahk.execute
  (maybe some kind of subroutine wrapper?).
* Add examples directory.
* Add optional unicode support.

.. _LICENSES.txt: https://bitbucket.org/kitsu/pyahk/src/tip/LICENSES.txt
.. _AutoHotKey.dll: http://www.autohotkey.net/~HotKeyIt/AutoHotkey/files/AutoHotkey-dll-txt.html
.. _Python2.7: http://python.org/download/releases/2.7.3/#download 
.. _`mock library`: http://www.voidspace.org.uk/python/mock/
.. _Docs: http://kitsu_eb.pythonanywhere.com/docs/pyahk
.. _ReadTheDocs: http://read-the-docs.readthedocs.org/en/latest/getting_started.html
