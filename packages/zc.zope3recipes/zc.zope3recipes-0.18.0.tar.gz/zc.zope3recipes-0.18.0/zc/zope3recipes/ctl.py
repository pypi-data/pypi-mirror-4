##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Top-level controller for 'zopectl'.
"""

import os, sys
import zdaemon.zdctl

class ZopectlCmd(zdaemon.zdctl.ZDCmd):

    def do_debug(self, ignored_because_its_stupid):
        os.spawnlp(os.P_WAIT, self._debugzope, self._debugzope,
                   '-C', self._zope_conf,
                   *self.options.args[1:])

    def help_debug(self):
        print "debug -- Initialize the Zope application, providing a"
        print "         debugger object at an interactive Python prompt."

    do_run = do_debug

    def help_run(self):
        print "run <script> [args] -- run a Python script with the Zope "
        print "                       environment set up.  The script has "
        print "                       'root' exposed as the root container."


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    class Cmd(ZopectlCmd):
        _debugzope = args.pop(0)
        _zope_conf = args.pop(0)

    zdaemon.zdctl.main(args, None, Cmd)
