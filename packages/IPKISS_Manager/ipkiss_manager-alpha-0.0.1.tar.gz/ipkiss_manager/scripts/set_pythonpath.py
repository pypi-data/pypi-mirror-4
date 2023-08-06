
"""
    This script sets the current ipkiss installation installation
    in the PYTHONPATH system variable
"""

import os
import subprocess

from ipkiss_manager.manager import RefManager

r = RefManager()

try:
    ipkiss_path = r.local_references['in_use_ipkiss']
except Exception, e:
    print "Error on loading register:", e
    exit()

try:
    pp = os.environ['PYTHONPATH']

    if os.name == 'nt': #windows
        pp = pp + ';%s' % ipkiss_path
    else:   #linux
        pp = pp + ':%s' % ipkiss_path

except KeyError:
    pp = ipkiss_path


if os.name == 'nt': #windows
    command = "setx %s" % pp
else:   #linux
    command = "export PYTHONPATH=%s" % pp

subprocess.call(command.split(), shell=True)
