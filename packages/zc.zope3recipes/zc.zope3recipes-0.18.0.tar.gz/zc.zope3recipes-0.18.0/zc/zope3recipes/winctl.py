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
import socket
import subprocess
import errno
import zdaemon.zdctl
from zdaemon.zdctl import ZDCmd
from zdaemon.zdoptions import ZDOptions
from ZConfig.components.logger.handlers import FileHandlerFactory
from ZConfig.datatypes import existing_dirpath

if sys.platform[:3].lower() == "win":
    import win32api
    import win32com.client
    import win32process
    from win32file import ReadFile, WriteFile
    from win32pipe import PeekNamedPipe
    import msvcrt
    import select


def getChildrenPidsOfPid(pid):
    """Returns the children pids of a pid"""
    wmi = win32com.client.GetObject('winmgmts:')
    children = wmi.ExecQuery('Select * from win32_process where ParentProcessId=%s' % pid)
    pids = []
    for proc in children:
        pids.append(proc.Properties_('ProcessId'))
    return pids


def getDaemonProcess(pid):
    """Returns the daemon proces."""
    wmi = win32com.client.GetObject('winmgmts:')
    children = wmi.ExecQuery('Select * from win32_process where ProcessId=%s' % pid)
    pids = []
    for proc in children:
        pids.append(proc.Properties_('ProcessId'))
    if len(pids) == 1:
        return pids[0]
    return None


def getZopeScriptProcess(pid):
    """Returns the daemon proces."""
    wmi = win32com.client.GetObject('winmgmts:')
    children = wmi.ExecQuery('Select * from win32_process where ParentProcessId=%s' % pid)
    pids = []
    for proc in children:
        pids.append(proc.Properties_('ProcessId'))
    if len(pids) == 1:
        return pids[0]
    return None


def kill(pid):
    """kill function for Win32"""
    handle = win32api.OpenProcess(1, 0, pid)
    win32api.TerminateProcess(handle, 0)
    win32api.CloseHandle(handle)


def killAll(pid):
    """Kill runzope and the python process started by runzope."""
    pids = getChildrenPidsOfPid(pid)
    for pid in pids:
        kill(pid)


class Popen(subprocess.Popen):
    def recv(self, maxsize=None):
        return self._recv('stdout', maxsize)

    def recv_err(self, maxsize=None):
        return self._recv('stderr', maxsize)

    def send_recv(self, input='', maxsize=None):
        return self.send(input), self.recv(maxsize), self.recv_err(maxsize)

    def get_conn_maxsize(self, which, maxsize):
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return getattr(self, which), maxsize

    def _close(self, which):
        getattr(self, which).close()
        setattr(self, which, None)

    def send(self, input):
        if not self.stdin:
            return None

        try:
            x = msvcrt.get_osfhandle(self.stdin.fileno())
            (errCode, written) = WriteFile(x, input)
        except ValueError:
            return self._close('stdin')
        except (subprocess.pywintypes.error, Exception), why:
            if why[0] in (109, errno.ESHUTDOWN):
                return self._close('stdin')
            raise

        return written

    def _recv(self, which, maxsize):
        conn, maxsize = self.get_conn_maxsize(which, maxsize)
        if conn is None:
            return None

        try:
            x = msvcrt.get_osfhandle(conn.fileno())
            (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
            if maxsize < nAvail:
                nAvail = maxsize
            if nAvail > 0:
                (errCode, read) = ReadFile(x, nAvail, None)
        except ValueError:
            return self._close(which)
        except (subprocess.pywintypes.error, Exception), why:
            if why[0] in (109, errno.ESHUTDOWN):
                return self._close(which)
            raise

        if self.universal_newlines:
            read = self._translate_newlines(read)
        return read


# TODO: implement a win service script and add install and remove methods for
# the service.
# Also implement start and stop methods controlling the windows service daemon
# if the service is installed. Use the allready defined methods if no service
# is installed.

#class ZopeCtlOptions(ZDOptions):
#    """Zope controller options."""
#
#    def realize(self, *args, **kwds):
#        ZopeCtlOptions.realize(self, *args, **kwds)
#
#        # Add the path to the zopeservice.py script, which is needed for
#        # some of the Windows specific commands
#        servicescript = os.path.join(self.directory, 'bin', 'zopeservice.py')
#        self.servicescript = '"%s" %s' % (self.python, servicescript)


class ZopectlCmd(zdaemon.zdctl.ZDCmd):
    """Manages Zope start and stop etc.

    This implementation uses a subprocess for execute the given python script.

    There is also a windows service daemon which can get installed with the
    install and remove  methods. If a windows service is installed, the
    controller dispatches the start and stop commands to the service. If no
    service is installed, we use the subprocess instead.
    """

    zd_up = 0
    zd_pid = 0
    zd_status = None
    proc = None

    def do_install(self, arg):
        """Install the windows service."""
        #program = "%s install" % self.options.servicescript
        #print program
        #subprocess.Popen(program)
        print "Not implemented right now"

    def help_install(self):
        print "install -- Installs Zope3 as a Windows service."
        print "Not implemented right now"

    def do_remove(self, arg):
        """Remove the windows service."""
        #program = "%s remove" % self.options.servicescript
        #print program
        #subprocess.Popen(program)
        print "Not implemented right now"

    def help_remove(self):
        print "remove -- Removes the Zope3 Windows service."
        print "Not implemented right now"

    def do_debug(self, arg):
        # Start the process
        if self.zd_pid:
            print "Zope3 already running; pid=%d" % self.zd_pid
            return
        args  = " ".join(self.options.args[1:])
        cmds = [self._debugzope, '-C', self._zope_conf, args]
        program = " ".join(cmds)
        print "Debug Zope3: ", program
        self.proc = Popen(program)
        self.zd_pid = self.proc.pid
        self.zd_up = 1
        self.awhile(lambda: self.zd_pid,
                    "Zope3 started in debug mode, pid=%(zd_pid)d")

    def help_debug(self):
        print "debug -- Initialize the Zope application, providing a"
        print "         debugger object at an interactive Python prompt."

    do_run = do_debug

    def help_run(self):
        print "run <script> [args] -- run a Python script with the Zope "
        print "                       environment set up.  The script has "
        print "                       'root' exposed as the root container."

    def send_action(self, action):
        """Dispatch actions to subprocess."""
        try:
            self.proc.send(action + "\n")
            response = ""
            while 1:
                data = self.proc.recv(1000)
                if not data:
                    break
                response += data
            return response
        except (subprocess.pywintypes.error, Exception):
            return None

    def get_status(self):
        if not self.zd_pid:
            return None
        proc = getDaemonProcess(self.zd_pid)
        if proc is not None:
            self.zd_up = 1
        proc = getZopeScriptProcess(self.zd_pid)
        if proc is not None:
            self.zd_status = "Zope3 is running"
            return self.zd_status
        return None

    def do_stop(self, arg):
        # Stop the Windows process
        if not self.zd_pid:
            print "Zope3 is not running"
            return

        killAll(self.zd_pid)
        self.zd_up = 0
        self.zd_pid = 0
        cpid = win32process.GetCurrentProcessId()
        self.awhile(lambda: not getChildrenPidsOfPid(cpid), "Zope3 stopped")

    def do_kill(self, arg):
        self.do_stop(arg)

    def do_restart(self, arg):
        pid = self.zd_pid
        if self.zd_pid:
            self.do_stop(arg)
            self.do_start(arg)
        else:
            self.do_start(arg)
        self.awhile(lambda: self.zd_pid not in (0, pid),
                    "Zope3 restarted, pid=%(zd_pid)d")

    def show_options(self):
        print "winctl options:"
        print "configfile:  ", repr(self.options.configfile)
        print "python:      ", repr(self.options.python)
        print "program:     ", repr(self.options.program)
        print "user:        ", repr(self.options.user)
        print "directory:   ", repr(self.options.directory)
        print "logfile:     ", repr(self.options.logfile)

    def do_start(self, arg):
        # Start the process
        if self.zd_pid:
            print "Zope3 already running; pid=%d" % self.zd_pid
            return
        program = " ".join(self.options.program)
        print "Starting Zope3: ", program
        self.proc = Popen(program)
        self.zd_pid = self.proc.pid
        self.zd_up = 1
        self.awhile(lambda: self.zd_pid,
                    "Zope3 started, pid=%(zd_pid)d")

    def do_fg(self, arg):
        self.do_foreground(arg)

    def help_fg(self):
        self.help_foreground()

    def do_foreground(self, arg):
        # Start the process
        if self.zd_pid:
            print "To run the Zope3 in the foreground, please stop it first."
            return

        program = self.options.program + self.options.args[1:]
        program = " ".join(program)
        sys.stdout.flush()
        try:
            subprocess.call(program)
            print "Zope3 started in forground: ", program
        except KeyboardInterrupt:
            print

    def help_foreground(self):
        print "foreground -- Run the program in the forground."
        print "fg -- an alias for foreground."
        print "Not supported on windows will call start"


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    class Cmd(ZopectlCmd):
        _debugzope = args.pop(0)
        _zope_conf = args.pop(0)

    zdaemon.zdctl.main(args, None, Cmd)
