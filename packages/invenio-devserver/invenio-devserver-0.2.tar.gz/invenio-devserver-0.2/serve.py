import sys
import inspect
import os

SRC_PATH = "src"

# Script directory
directory = os.path.dirname(inspect.getfile(inspect.currentframe()))
if not directory:
    directory = '.'
directory = os.path.abspath("%s/%s" % (directory, SRC_PATH))
sys.path.append(directory)

from invenio_devserver import serve
serve.main()
