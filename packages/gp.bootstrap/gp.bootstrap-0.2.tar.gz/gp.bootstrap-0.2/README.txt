Create a ``~/.buildout/default.cfg`` if it doesn't exist

Create a ``buildout.cfg`` based on ``~/.buildout/template.cfg`` if it doesn't exist

Download the ``bootstrap.py`` script if needed.

Then run ``bin/buildout``.

Example::

  $ bootstrap           # bootstrap with sys.executable

  $ bootstrap 2.5       # bootstrap with python2.5

  $ bootstrap 2.5 -vvv  # extra buildout options

