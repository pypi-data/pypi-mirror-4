import sys


# define a function to handle str types
if sys.version < '3':
    import codecs

    def u(text):
        # return a unicode text
        return codecs.unicode_escape_decode(text)[0]
else:
    def u(text):
        # leave text as it is
        return text


def print_text(text, *args, **kwargs):
    """Print a text to standar output

    """
    if text:
        end = kwargs.pop('end', '\n')
        if args:
            text = (text % args) + end
        else:
            text = text + end

    sys.stdout.write(text)


def get_exception_obj():
    """Get Exception instance in the context of an exception

    """
    return sys.exc_info()[1]


def get_exception_info():
    """Get a "3-uple" with exception information

    Tuple contains (Exception class, Exception instance, traceback).

    """
    return sys.exc_info()
