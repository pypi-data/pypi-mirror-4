import logging
import os
import shutil
import stat
import tempfile

from subprocess import PIPE
from subprocess import Popen

JAVA_BIN = 'java'
YUI_JAR = 'yuicompressor.jar'

LOG = logging.getLogger('shrink')


def init_logging(options=None):
    """Init script logging

    """
    kw = {
        'format': '%(levelname)-5.5s %(message)s',
        'level': logging.INFO,
    }
    if options:
        if options.quiet:
            kw['level'] = logging.ERROR
        elif options.debug:
            kw['level'] = logging.DEBUG

    logging.basicConfig(**kw)


def yuicompress(in_file_name, out_file_name, java_bin=None, yui_jar=None):
    """Run yuicompressor script for a file

    Runs compressor script and store result in a tuple with compressor
    script return code and output.
    Output is the error string when return code is not zero.

    Return a tuple with (result_code, output_str).

    """
    # set some sane default values
    if not java_bin:
        java_bin = JAVA_BIN
    if not yui_jar:
        yui_jar = YUI_JAR

    LOG.info('Generating file %s', out_file_name)
    #get compression type from file extension (css, js)
    file_type = os.path.splitext(out_file_name)[1]
    file_type = file_type.lstrip('.')

    cmd = [java_bin, '-jar', yui_jar, '-o', out_file_name,
           '--type', file_type, in_file_name]
    LOG.debug('Executing: %s', ' '.join(cmd))

    #create a process to run compressor and
    #dont display command output to console
    popen = Popen(cmd, stdout=PIPE, stderr=PIPE)
    return_code = popen.wait()

    #after process finishes get command output
    if return_code:
        output_str = popen.stderr.read()
    else:
        output_str = popen.stdout.read()

    return (return_code, output_str)


def get_absolute_path(directory, file_name):
    """Get absolute path for a file

    """

    relative_path = os.path.join(directory, file_name)

    return os.path.abspath(relative_path)


def join_files(file_name_list):
    """Join a list of files into a single temporary file

    Each file is treated as text file.

    Return a string with temporary file name and path.

    """
    failed = False
    #create a temporary file to concatenate file contents
    (tmp_file_fd, tmp_file_name) = tempfile.mkstemp(text=True)
    LOG.debug('Created temporary file %s for join', tmp_file_name)

    #use given file descriptor to open file
    tmp_file = os.fdopen(tmp_file_fd, 'w')

    #concatenate each file in list into the temporary file
    for file_name in file_name_list:
        if not os.path.isfile(file_name):
            LOG.error('Invalid file %s for concatenation', file_name)
            failed = True
            break

        src_file = None
        try:
            LOG.debug('Adding %s to temporary file', file_name)
            src_file = open(file_name, 'r')
            #copy file contents into temp file
            shutil.copyfileobj(src_file, tmp_file)
        except Exception:
            LOG.exception('Unable to concatenate file %s', file_name)
            failed = True
            #close current opened file
            if src_file:
                src_file.close()

            break

        #always close opened files when no exception are raised
        if src_file:
            src_file.close()

    tmp_file.close()
    if failed:
        #remove temp file before exit
        os.remove(tmp_file_name)
        LOG.debug('Deleted temporary file %s', tmp_file_name)

        return False
    else:
        # change read and write permissions on temp file
        owner_rw = (stat.S_IRWXU & ~stat.S_IXUSR)
        group_rw = (stat.S_IRWXG & ~stat.S_IXGRP & ~stat.S_IWGRP)
        others_rw = (stat.S_IRWXO & ~stat.S_IXOTH & ~stat.S_IWOTH)
        os.chmod(tmp_file_name, owner_rw | group_rw | others_rw)

    return tmp_file_name


def get_data_dir():
    """Get absolute path for data directory

    """
    return os.path.join(os.path.dirname(__file__), 'data')


def get_data_file(file_name):
    """Get path for a file in data directory

    """
    data_dir = get_data_dir()

    return os.path.join(data_dir, file_name)
