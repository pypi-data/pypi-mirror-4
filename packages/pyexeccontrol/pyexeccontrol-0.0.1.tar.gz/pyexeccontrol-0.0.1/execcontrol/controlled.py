from __future__ import print_function
from pexpect import spawn
from pty import openpty
import threading
import os
from logging import info
import logging
import sys

logging.basicConfig(level=logging.DEBUG)

from parse_gdb_mi import infoline

class PrintStream(threading.Thread):

    def __init__(self, stream_descriptor, lineHandler=print):
        self.file = os.fdopen(stream_descriptor)
        threading.Thread.__init__(self)
        self.lineHandler = lineHandler

    def run(self):
        info("PrintStream started")
        while True:
            line = self.file.readline()
            if not line: break
            info ("line from stream: %s " % line)
            self.lineHandler (line)
        info("PrintStream exited")

class ControlledExec(object):

    def wait_prompt(self):
        self.debug_console.expect ("\(gdb\)")

    def __init__(self, exec_path, logfile = None, out_stream_handler = print):
        self.exec_path = exec_path
        self.out_stream_handler = out_stream_handler
        # allocate a pty for controlling
        self.master, self.slave = openpty()
        exec_string = "gdb %s -tty %s -interpreter mi" % (self.exec_path,os.ttyname(self.slave))
        info("starting %s" % exec_string)
        self.debug_console = spawn(exec_string, logfile = logfile)
        self.wait_prompt()

    def run_stream_handler(self):
        self.print_stream_handler = PrintStream(self.master,lineHandler = self.out_stream_handler)
        self.print_stream_handler.daemon = True
        self.print_stream_handler.start()

    def run_command(self, cmd):
        outstring = ""
        outstring += self.console_command(cmd)
        self.wait_prompt()


    def get_parsed_info(self,cmd):
        out = self.console_cmd(cmd)
        info = out.splitlines()[2]
        return infoline.parseString(info).asList()[1]

    def thread_info(self):
        return self.get_parsed_info("-thread-info")


    def get_variables(self):
        return self.get_parsed_info("-stack-list-variables 2")

    def get_file_info(self):
        return self.get_parsed_info("-file-list-exec-source-file")

    def exec_run(self):
        self.console_cmd("-exec-run")
        self.wait_prompt()

    def close(self):
        self.debug_console.close()


    def exec_continue(self):
        self.console_cmd("-exec-continue")
        self.wait_prompt()

    def next(self):
        self.console_cmd("-exec-next")
        self.wait_prompt()

    def console_cmd(self, cmd):
        self.debug_console.sendline(cmd)
        self.wait_prompt()
        return self.debug_console.before

    def set_break(self, point):
        return self.console_cmd("-break-insert %s" % point)

    def run_inferior(self):
        child = self.debug_console
        self.run_stream_handler()
        child.expect("\(gdb\)")
        child.sendline("-exec-run")
        child.expect(".*exited.*")
        child.sendline("quit")
        child.readlines()

