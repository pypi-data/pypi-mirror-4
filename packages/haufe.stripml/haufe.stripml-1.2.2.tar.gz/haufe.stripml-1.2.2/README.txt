=====================
Package haufe.stripml
=====================

Python extension for stripping HTML markup from text.

This package simply removes HTML-like markup from text in a very quick and
brutal manner. It could quite easily be used to strip XML or SGML from text as
well. It does not do any syntax checking.

The core functionalities are implemented with the C++ programming language, and
thus much quicker than using SGMLParser or regular expressions for the same
task.


Copyright
---------
haufe.stripml is (C) Tobias Rodaebel & Haufe Mediengruppe, D-79111 Freiburg, Germany


Licence
-------
This package is released under the LGPL 3 See LICENSE.txt.


Installation
------------

Use easy_install::

  easy_install haufe.stripml


Testing
-------

haufe.stripml can be tested by typing::

  python setup.py test -m haufe.stripml.tests


Credits
-------
Thanks to Gottfried Ganssauge for translating to the C++ programming language.
