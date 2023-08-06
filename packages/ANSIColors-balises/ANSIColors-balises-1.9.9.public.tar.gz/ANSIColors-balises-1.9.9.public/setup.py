#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from distutils.core import setup

import ANSIColors

setup(name='ANSIColors-balises',
      version=ANSIColors.__version__,
      description='ANSIColors brings a simple and power full way to use colours in a terminal.',
      # long_description=open('README.rst').read()
      long_description="""
About
=====

Provide *efficient* and useful **functions** to use colours, in a *HTML-balise like style*.

Almost all ANSI Colours are defined with this balise-like style.
**This point is the main interest of this module,**
because many others defines function to print with some colours.

The **reset** balise is a special balise to reinitialize all previously changed parameters.

Colours
=======

Foregrounds
-----------

You can choose one of the 8 basic ANSI colours: black, red, green, yellow, blue,
magenta, cyan, white.
The names beginning with a *lowerscript* design **foreground** colours.

For example ::

 ANSIColors.printc('<reset>this is default. <red>this is red<yellow> and yellow in foreground now<reset>').

Backgrounds
-----------

You can choose one of the 8 basic ANSI colours: Black, Red, Green, Yellow, Blue,
Magenta, Cyan, White.
The names beginning with a *upperscript* design **background** colors.

For example ::

 ANSIColors.printc('<Default>this is default. <Blue>this have a blue background<Black> and black in background now<reset>').

Other balises
-------------

The following balises are also available :
 * ``italic``, ``Italic`` : to turn on and off the *italic* mode (not always supported),
 * ``b``, ``B`` : to turn on and off the *bold* mode (not always supported),
 * ``u``, ``U`` : to turn on and off the *underline* mode (not always supported),
 * ``neg``, ``Neg`` : to turn on and off the *reverse video* mode,
 * ``blink``, ``Blink`` : to turn on and off the *blink* mode (not always supported),
 * ``el`` : to erase the current line,
 * ``bell`` : to make the terminal's bell ring (not always supported).

Macros
------

Some macros are also provided, like the balises ``<ERROR>``, ``<INFO>`` or ``<WARNING>``.

And also ``<warning>`` and ``<question>``, which respectivly give a colored ``!`` and ``?``.

Writing to a file
-----------------

This is possible with the ``writec`` function. For example ::

 import sys
 ANSIColors.writec('<ERROR><u><red>The computer is going to explode!<reset>', fn=sys.stderr)
 # sys.stderr.flush()
 # this is useless : writec flush itself.

Auto detection
==============

Of course, the colours are disabled if the output doesn't support them.

It works perfectly on GNU/Linux (Ubuntu 11.10) and Windows (with or without Cygwin),
and have *not* be tested on MAC OS X or on other UNIX-like.

Other features
===============

Others functions
-----------------

Provide also the ``xtitle`` function, to change the title of the terminal.
This try to use the command *xtitle*, and next try to use *ANSI Code* to change the title.

And a ``notify`` function to display a system notification (using ``notify-send``).

Script
------

``ANSIColors.py`` is also a script.
You can have his description (or use it) directly with ::

 python -m ANSIColors --help

For testing
~~~~~~~~~~~

It can be used to run some tests (with the --test option).

With GNU/Bash
~~~~~~~~~~~~~

It can be used to generate a GNU/Bash colour profile
(with the ``--generate --file colour.sh`` options).

This ``sh`` file can be imported with ``$ . colour.sh`` in any GNU/Bash scripts,
or even in your ``~/.bashrc`` file.

License
=======

 This module is licensed under the term of the **GNU Public License**, version 3 (*GPLv3*).
 See the file *LICENSE* for more details.
""",
      author='Lilian Besson (for Naereen CORP.)',
      author_email='naereen-corporation@laposte.net',
      url='https://www.bitbucket.org/lbesson/ansi-colors',
      download_url='https://sites.google.com/site/naereencorp/tools/ansi-colors',
      license='GPLv3',
      platforms=['Windows', 'Windows Cygwin', 'GNU/Linux'],
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: User Interfaces',
          'Topic :: Terminals',
          'Topic :: Utilities'
          ],
      py_modules=['ANSIColors'],
     )