c = get_config()
app = c.InteractiveShellApp

# This can be used at any point in a config file to load a sub config
# and merge it into the current one.
load_subconfig('ipython_config.py', profile='default')

lines = """
import sys, os
os.environ['R_LIBS_USER'] = '/home/yonatanf/R/x86_64-unknown-linux-gnu-library/2.12'
import cPickle as pickle
import survey2
from survey2 import *
"""

# You have to make sure that attributes that are containers already
# exist before using them.  Simple assigning a new list will override
# all previous values.

if hasattr(app, 'exec_lines'):
    app.exec_lines.append(lines)
else:
    app.exec_lines = [lines]

