import os

VERSION_INFO = {
    'major': 1,
    'minor': 1,
    'micro': 1,
}


def get_version(short=False):
    """Get a string with app version.

    """
    version = "%(major)i.%(minor)i" % VERSION_INFO
    # append micro version only if not short and micro != 0
    if not short and VERSION_INFO['micro']:
        version = version + (".%(micro)i" % VERSION_INFO)

    return version


def read_file(*path):
    """Read and return all contents of a text file

    """
    full_path = os.path.join(*path)
    file_obj = open(full_path)
    try:
        return file_obj.read()
    finally:
        file_obj.close()


__version__ = get_version()
