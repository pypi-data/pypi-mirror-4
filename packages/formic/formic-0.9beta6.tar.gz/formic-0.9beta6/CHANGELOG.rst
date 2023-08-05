Changelog
=========

0.9beta6
--------

* Fixed issue #2: VERSION.txt was not being correctly packaged causing problems
  with source and pip installation
* Fixed issue #3: Incorrect behaviour when absolute directory was "/"
* Removed Google Analytics from documentation, and improved documentation template
* Improved publishing process.

0.9beta5
--------

This is a documentation and SCM release. No API changes.

* Updated documentation, changelogs and installation instructions
* Removed Google Analytics from Sphinx documentation
* Implemented `Dovetail <http://www.aviser.asia/dovetail>`_ build
  * Added coverage, pylint and sloccount metrics generation
  * Added command-line sanity tests

0.9beta4
--------

* Fixed issue `#1 <https://bitbucket.org/aviser/formic/issue/1/an-include-like-py-does-not-match-files>`_:
  In `3de0331450c0 <https://bitbucket.org/aviser/formic/changeset/3de0331450c0>`_

0.9beta3
--------

* API: FileSet is now a natural iterator::

    fs = FileSet(include="*.py")
    filenames = [ filename for filename in fs ]

* API: ``__str__()`` on Pattern and FileSet has been improved. Pattern now
  returns the just normalized string for the pattern (eg ``**/*.py``). FileSet
  now returns the details of the set include all the include and exclude
  patterns.

* Setup: Refactored setup.py and configuration to use only setuptools (removing
  distribute and setuptools_hg)

* Documentation: Renamed all ReStructured Text files to .rst. Small
  improvements to installation instructions.


0.9beta2
--------

* Refactored documentation files and locations to be more DRY:

  * Sphinx documentation
  * setup.py/Pypi readme
  * README/INSTALL/CHANGELOG/USAGE in topmost directory

* Removed the file-based distribute depending on explicit dependency
  in setup.py

0.9beta
-------

Date: 14 Apr 2011
First public release