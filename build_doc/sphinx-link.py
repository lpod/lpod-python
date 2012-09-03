import sys
from pkg_resources import load_entry_point

entry_point = load_entry_point('Sphinx>=0.6.1', 'console_scripts',
                               'sphinx-build')
sys.exit(entry_point())
