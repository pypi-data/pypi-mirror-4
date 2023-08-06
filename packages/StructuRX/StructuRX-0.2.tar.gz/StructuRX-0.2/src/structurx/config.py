import sys
import os

sys.path[:0] = [''] # not sure why we need this but something messes with the path
    # when running scripts

class ConfigurationError(Exception):
    pass

def show_settings_help():
    out = """
You should have a file 'structurx_settings.py' somewhere in your PYTHONPATH 
(such as the current working directory '%s') which contains the necessary settings,
such as:
CLEARPARSER_BASE = '/usr/local/clearparser'
CLEARPARSER_EXTRA = '/usr/local/clearparser/extra'

"""
    print >> sys.stderr, out % (os.getcwd())

try:
    import structurx_settings as settings
except ImportError, e:
    show_settings_help()
    raise ConfigurationError("No module 'structurx_settings' was found on "
        "the PYTHONPATH", e)

