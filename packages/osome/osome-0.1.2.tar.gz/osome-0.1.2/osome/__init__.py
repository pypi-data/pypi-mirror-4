import sys

if sys.version.startswith('3'):
    base_string_class = str
    python3 = True
else:
    base_string_class = unicode
    python3 = False

from osome.run import run
from osome.path import path
