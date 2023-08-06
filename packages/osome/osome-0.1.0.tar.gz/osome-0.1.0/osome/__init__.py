import sys

if sys.version.startswith('3'):
    base_string_class = str
else:
    base_string_class = unicode

from osome.run import run
from osome.path import path
