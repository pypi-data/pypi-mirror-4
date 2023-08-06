#
# A script that registers Coopr COM servers
#
#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

import sys
if sys.version_info[0:2] < (2,4):
    print ""
    print "ERROR: Pyomo requires Python 2.4 or newer"
    sys.exit(1)
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__))))
sys.path.append(".")
import os
import commands
import coopr.pyomo.main_script
import pyutilib.misc

# NEVER copy the following ID
# Use "print pythoncom.CreateGuid()" to make a new one.

class PyomoCOMInterface:
    _public_methods_ = [ 'XRun', 'Run' ]
    _reg_progid_ = "Coopr.Pyomo"
    _reg_clsid_ = "{A07BB601-AB93-4379-8D69-01C2B0F08601}"

    def Run(self, directory, modelfile, datascript, logfile):
        try:
            pyutilib.misc.setup_redirect(logfile)
            sys.argv.append("--summary")
            sys.argv.append("--log")
            sys.argv.append(directory+os.sep+modelfile)
            sys.argv.append(directory+os.sep+datascript)
            coopr.pyomo.main_script.run()
            pyutilib.misc.reset_redirect()
            return logfile
        except Exception, err:
            return str(err)
        except BaseException, err:
            return str(err)
        except:
            pass
        return "Unknown Error"

    def XRun(self, directory, modelfile, datascript):
        cmd = "pyomo "+directory+os.sep+modelfile+" "+directory+os.sep+datascript
        return cmd


if __name__=='__main__':
    print "Registering Coopr.Pyomo COM server..."
    import win32com.server.register
    win32com.server.register.UseCommandLine(PyomoCOMInterface)
