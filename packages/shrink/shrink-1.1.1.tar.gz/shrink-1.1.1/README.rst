========
 Shrink
========

Shrink is a command for concatenating and compressing css stylesheets and
javascript files making them smaller.
Shrinking (or minifying) these files reduces the number of request that are
made after a page load and also the size of these requests.

This command depends on `YUI Compressor`_ for compression, and runs with
Python 2.5 and above, including Python 3.

Install
=======

Shrink can be easily installed from pypi by running::

  $ pip install shrink

After install is good to display script information and options::

  $ shrink -h

.. _YUI Compressor: http://developer.yahoo.com/yui/compressor/

Config file
===========

``INI`` style files are used to know which files will be minified, set some
global options and also to know which files will be joined before
minification.

A good starting point to get familiar with Shrink config file format is to
read the example shrink config file. To create an example file run::

  $ shrink --example-cfg

This command creates a file called ``example_shrink.cfg`` in current folder.

Config file format
==================

Config file has a section for each individual file that can be generated,
and on top it also has a special section called ``DEFAULT`` where global
options are defined.

Global ``DEFAULT`` options:

 * ``base_dir`` defines a base directory used as prefix to find static files.
   This value can be referenced in any other section using the python variable
   notation ``%(base_dir)s``.
 * ``hash_dir`` defines a folder where ``shrink.sha1`` file is stored. See
   `Shrink hash file`_ for more info. By default, this file is stored in the
   same folder where shrink config file is located.
 * ``arg.*`` defines default values for some command line argumens. Supported
   arguments are ``arg.java_bin`` and ``arg.yui_jar``.
   The values given here are overriden by the ones given during runtime as
   command line arguments.

Each file section has some options that are used during join, compression and
hashing of a file. These file section options are:

 * ``source_directory`` value defines the folder where file(s) listed in
   ``source_files`` are located.
 * ``source_files`` value can be a single file name, or a list of file names.
   When a list of names is given, each file in list is concatenated (from top
   to down) into a single file before compression.
 * ``destination_directory`` value sets output directory for the minified file
   By default minified file is generated in source directory.
 * ``destination_file`` value is the name for the minified file.
 * ``hash`` is a boolean value. When it is true destination file is included
   during shrink hash generation. See `Shrink hash file`_.
 * ``compress`` is a boolean value. Destination file is not compressed when
   this value is false. By default compression is done for destination
   files.
   This option is useful when is desirable to join many files without
   compressing them because they are already compressed.

For example, a section for minifying a file called ``sample-file.js`` could
be written as::

  [sample-single-file-js]
  source_directory = %(base_dir)s/js
  destination_file = sample-file.min.js
  source_files = sample-file.js

Final minified file name would be ``sample-file.min.js``.

Many files can also be specified to be joined into a single file before
compression by writing a section like::

  [sample-multiple-file-css]
  source_directory = %(base_dir)s/css
  destination_file = sample-multiple-file.min.css
  source_files =
      sample-file1.css
      sample-file2.css
      sample-file3.css

Generated file name is given by ``destination_file`` value.

Minimize css and js files
=========================

To minify all files, run::

  $ shrink -f example_shrink.cfg all

This will use ``yuicompressor.jar`` and the ``example_shrink.cfg`` file in
current directory to compress all files.

In case that minification is not desired for all files, is also possible to
minify individual files, or a group of files (See `Section groups`_), by
using the name(s) of each section instead of ``all`` as argument.

To list available sections, run::

  $ shrink -f example_shrink.cfg -l

Section groups
--------------

Instead of running script with ``sample-single-file-js`` and
``sample-multiple-file-css`` as arguments is possible to define a group like::

  [sample-group]
  group =
      sample-single-file-js
      sample-multiple-file-css

And then run minifier script with ``sample-group`` as the only parameter.

Shrink hash file
----------------

After minification Shrink can create a file containing a SHA1 hash. The file
is created when at least one section in config file has ``hash = true``. Hash
is created using the contents of all destination files in these sections.

This is useful to know when some files changed, and to reload static css and
javascript files without using a timestamp or version number.
Sometime can be desirable to reload modified static files without increasing
application version. In these cases the hash can be used as request parameter
instead of version number.

Deployment notes
================

It can happen your application stop working or have unespected results when
it is deployed with minified css and javascript files.
Many times some of these problems are is easy avoid by having present the
following notes during ``shrink.cfg`` setup:

 * The order of the source files in each config section must be the same as
   the one in your HTML templates.
 * CSS files normally contains URLs which are relative to the location of
   the file where they are declared. So for these cases the location for
   destination file must be the same as the one for source files.
   Some javascript files might define some path or URL that might also be
   relative to a file location.
 * Check that all files wich are NOT minified are being included in your
   HTML template.
