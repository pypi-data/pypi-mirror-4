import os
import subprocess
from ollitools.dev import obj_attr
from plumbum.local_machine import LocalPath

#lp = LocalPath(os.getcwd())
#print str(lp)
#print obj_attr(lp, filterMethods=False)
#print obj_attr(lp._path)

here = os.getcwd()
scriptPath = os.path.join(here, "loslassa.py")
os.chdir(os.path.join(here, "example_project"))
print os.getcwd()
subprocess.check_output([scriptPath, "play"])
os.chdir(scriptPath)
print os.getcwd()

