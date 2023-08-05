=========
Changelog
=========

1.1.1 - 2012-09-21
==================

 * Setup argument use_2to3 is now enabled only for python 3 series
 * Added ``Deployment notes`` to README file
 * Added read permissions to generated files for group and others

1.1.0 - 2012-07-31
==================

 * Added python 3 support
 * Updated documentation
 * Added initial files for unit testing

1.0.1 - 2012-07-19
==================

 * Added --hash-dir argument to allow changing hash file dir during runtime
 * Added ``compress`` INI file option to avoid compressing destination file
 * Added --example-cfg argument to create an example_shrink.cfg file in
   current folder

1.0.0 - 2012-07-11
==================

 * Added --version argument
 * Added SHA1 hashing support (``hash = true`` in any file section)
 * Added --hash-all argument to generae SHA1 hash using all files contents
