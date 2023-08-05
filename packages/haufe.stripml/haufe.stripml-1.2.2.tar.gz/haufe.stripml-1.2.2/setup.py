# psf: ta=4, -*-Python-*-, vi: set et ts=4:
"""Setup script for haufe.stripml."""
import os
import sys
try:
    from setuptools import setup, Extension
except ImportError:
    sys.stderr.write("Warning: setuptools not found; trying distutils.\n")
    from distutils.core import setup, Extension

version = open('version.txt').read().strip()
desc = open('README.txt').read() 
tests = open(os.path.join('haufe', 'stripml', 'README.txt')).read()
changes = open('CHANGES.txt').read()
long_description = desc+'\n\n'+tests+'\n=======\nChanges\n=======\n\n'+changes

setup (name = 'haufe.stripml',
       version = version,
       author  = 'Tobias Rodaebel',
       author_email = 'rodaebel@users.sourceforge.net',
       maintainer = 'Tobias Rodaebel',
       maintainer_email = 'rodaebel@users.sourceforge.net',
       license = 'LGPL 3',
       description = 'Python extension for removing markup from strings.',
       long_description = long_description,
       url = 'http://pypi.python.org/pypi/haufe.stripml',
       packages = ['haufe', 'haufe.stripml'],
       include_package_data = True,
       package_data = {'haufe.stripml': ['README.txt']},
       namespace_packages = ['haufe'],
       ext_modules = [
           Extension (
               '.'.join (('haufe', 'stripml', 'stripml')),
               sources = [os.path.join ('haufe', 'stripml', 'stripml.cpp')])
       ], 
       zip_safe = False,
       test_suite='nose.collector',
       test_requires=('nose',),
       install_requires=['setuptools'],
       platforms = ['All'],
       classifiers = [
           'Development Status :: 5 - Production/Stable',
           'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
           'Intended Audience :: Developers',
           'Operating System :: OS Independent',
           'Programming Language :: Python',
           'Programming Language :: C++',
           'Topic :: Software Development :: Libraries :: Python Modules',
           'Topic :: Text Processing :: Markup :: HTML',
           'Topic :: Text Processing :: Markup :: SGML',
           'Topic :: Text Processing :: Markup :: XML',
       ],
       keywords = [
           'SGML', 'HTML', 'XML', 'XHTML', ],)
