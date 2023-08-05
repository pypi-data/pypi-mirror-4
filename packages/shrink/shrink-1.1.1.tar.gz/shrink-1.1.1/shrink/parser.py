import hashlib
import logging
import os
import shutil

try:
    import configparser
except ImportError:
    configparser = __import__("ConfigParser")

from shrink import utils

OPEN_FILE_ERROR = 'Unable to open file %s'

LOG = logging.getLogger('shrink')


class ParserError(Exception):
    """Parser exception class

    """


class Parser(object):
    """Shrink ini file parser class

    """
    def __init__(self, cfg_file, args):
        self.cfg_file_dir = os.path.dirname(cfg_file)
        self.cfg_parser = self.get_config_parser(cfg_file)
        self.cfg_defaults = self.cfg_parser.defaults()
        self.args = self.update_default_arguments(args)
        self.sha1_hash = hashlib.sha1()
        # set hash file directory
        self.sha1_dir = self.get_sha1_dir()
        # when true a sha1 file is generated after minification
        self.sha1_updated = False

    def get_sha1_dir(self):
        """Get the full directory path for sha1 file

        """
        hash_dir = self.args.hash_dir
        if not hash_dir:
            hash_dir = (self.cfg_defaults.get('hash_dir') or '')
            # replace "here" variable with config file dir
            hash_dir = hash_dir % {'here': self.cfg_file_dir}

        # when no hash dir is given use config file directory
        return (hash_dir or self.cfg_file_dir)

    def get_config_parser(self, cfg_file):
        """Get a new ini file parser

        Parser is initialized with the given file information.

        """
        # init some default config parser variable values
        cfg_defaults = {'here': self.cfg_file_dir}
        # read config file options
        cfg_parser = configparser.ConfigParser(defaults=cfg_defaults)
        try:
            cfg_parser.read(cfg_file)
        except Exception:
            # print traceback only when debug flag is present
            LOG.exception('Config file is not valid')

            raise ParserError('Unable to parse config file %s' % cfg_file)

        return cfg_parser

    def update_default_arguments(self, args):
        """Update default values for missing command arguments using config
        file default values

        """
        for (name, value) in self.cfg_defaults.items():
            #skip non argument values
            if not name.startswith('arg.'):
                continue

            # remove "arg." prefix for name to get argument name
            arg_name = name.replace('arg.', '')
            # when argument is missing use ini file value
            if getattr(args, arg_name, None) is None:
                LOG.debug('Setting arg %s=%s from ini', arg_name, value)
                setattr(args, arg_name, value)

        return args

    def update_sha1_hash(self, file_name, chunk_size=4096):
        """Update SHA1 hash object with file info

        """
        try:
            file_obj = open(file_name, 'rb')
        except Exception:
            if self.args.debug:
                LOG.exception(OPEN_FILE_ERROR, file_name)

            LOG.error('File %s not included in hash', file_name)
            return
        # get file contents in small chunks and update global hash
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break

            # update global hash object with current chunk digest
            chunk_digest = hashlib.sha1(chunk).hexdigest()
            self.sha1_hash.update(chunk_digest.encode('utf8'))
            self.sha1_updated = True

        file_obj.close()

    def save_sha1_hash(self):
        """Save shrink.sha1 file in base directory

        """
        digest = self.sha1_hash.hexdigest()
        file_name = os.path.join(self.sha1_dir, 'shrink.sha1')
        try:
            file_obj = open(file_name, 'w')
            file_obj.write(digest)
            file_obj.close()
            LOG.info('Saved hash file %s', file_name)
        except Exception:
            if self.args.debug:
                LOG.exception(OPEN_FILE_ERROR, file_name)

            raise ParserError('Unable to save hash to %s' % file_name)

    def parse_section(self, section_name):
        """Parse a config section and minify files for that section

        """
        LOG.debug('Parsing section [%s]', section_name)
        # create a dictionary with config file section values
        values = dict(self.cfg_parser.items(section_name))

        # check if current section is a section for a group
        # NOTE: including groups inside groups can lead to recursion
        if 'group' in values:
            LOG.debug('Parsing section group [%s]', section_name)
            section_name_list = values['group'].strip('\n').split('\n')
            for name in section_name_list:
                try:
                    self.parse_section(name)
                except configparser.NoSectionError:
                    msg = ('Invalid section name "%s" in section group [%s]'
                           % (name, section_name))

                    raise ParserError(msg)

            # after processing the group stop section processing
            return

        # check mandatory section option values
        for name in ('source_directory', 'destination_file', 'source_files'):
            if not values.get(name):
                msg = 'No %s value in section [%s]' % (name, section_name)

                raise ParserError(msg)

        # get section option values
        source_directory = values['source_directory']
        destination_file = values['destination_file']
        # by default source dir is used as destination dir
        destination_directory = values.get('destination_directory',
                                           source_directory)
        destination_file = utils.get_absolute_path(destination_directory,
                                                   destination_file)

        source_files = values['source_files'].strip('\n')
        source_file_list = [utils.get_absolute_path(source_directory,
                                                    file_name)
                            for file_name in source_files.split('\n')]

        # when a string with list of files is available
        # join them into one single file
        source_file_count = len(source_file_list)
        if source_file_count > 1:
            # source file name is now the temporary file
            # with contents of all files in group
            source_file = utils.join_files(source_file_list)
            if not source_file:
                msg = ('Unable to generate file %s for section [%s]'
                       % (destination_file, section_name))
                LOG.error(msg)

                return
        # when no files are joined just add directory to source file name
        elif source_file_list:
            source_file = source_file_list[0]
            source_file = utils.get_absolute_path(source_directory,
                                                  source_file)
        else:
            msg = 'Section [%s] dont have source file(s)' % section_name
            LOG.error(msg)

            return

        # check if source file has to be compressed (default is true)
        skip_compress = (values.get('compress', 'true') == 'false')
        if not skip_compress:
            # init keyword arguments for compress function
            kw = {}
            if self.args.java_bin:
                kw['java_bin'] = self.args.java_bin
            if self.args.yui_jar:
                kw['yui_jar'] = self.args.yui_jar

            # compress file and check if return code is not zero
            # when return code is not zero it means yuicompressor failed to run
            (return_code, out_str) = utils.yuicompress(source_file,
                                                       destination_file,
                                                       **kw)
        else:
            LOG.info('Generating file %s', destination_file)
            shutil.copy(source_file, destination_file)
            return_code = 0

        if return_code:
            LOG.error('Unable to generate %s', destination_file)
            # include yuicompressor error output
            if self.args.verbose:
                LOG.error(out_str)
        elif values.get('hash') or self.args.hash:
            # update sha1 hash object when file has to be included in hash
            self.update_sha1_hash(destination_file)

        # if files were joined into a single file remove
        #source file because is a temporary file
        if source_file_count > 1:
            os.remove(source_file)
            LOG.debug('Deleted temporary file %s', source_file)

    def get_section_names(self):
        """Get a list with all config file sections

        """
        # get section names sorted alphabetically
        section_name_list = self.cfg_parser.sections()
        section_name_list.sort()

        return section_name_list

    def list_all_sections(self):
        """List all sections in a config file

        """
        cfg_parser = self.cfg_parser
        section_name_list = self.get_section_names()
        # process each section
        for section_name in section_name_list:
            line = section_name
            is_section_group = cfg_parser.has_option(section_name, 'group')
            # when section is a group list sections inside that group
            if is_section_group:
                sub_sections = cfg_parser.get(section_name, 'group')
                sub_sections = sub_sections.strip('\n')
                sub_sections = sub_sections.replace('\n', ', ')

                line = '%s [%s]' % (line, sub_sections)

            yield line

    def parse(self):
        """Parse sections in a config file for the given arguments

        """
        section_name_list = self.get_section_names()
        #section name "all" means all sections are parsed
        parse_all = ('all' in self.args.sections)
        if parse_all:
            self.args.sections = section_name_list

        # process each section
        for section_name in section_name_list:
            is_section_group = self.cfg_parser.has_option(section_name,
                                                          'group')
            # if section name is not available as argument skip it, and also
            # skip section groups when all is available as script parameter
            skip_section = ((section_name not in self.args.sections)
                            or (parse_all and is_section_group))
            if not skip_section:
                self.parse_section(section_name)

        # finally generate the sha1 hash file in base directory
        if self.sha1_updated:
            self.save_sha1_hash()
