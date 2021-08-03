#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# G U I n s t a l l e r
#                                 an user friendly GUI interface for PyInstaller
#                                                            (C) jpl@ozf.fr 2021
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import subprocess
import psutil
import queue
import subprocess
import threading
import time
import traceback

from PyQt5.QtCore import QThread, pyqtSignal

import settings

#-------------------------------------------------------------------------------
# Class Shreald
# Shreald means "Shell in Thread"
#-------------------------------------------------------------------------------
class Shreald(QThread):

    linePrinted = pyqtSignal(str)

#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent, cmd, cwd, shell=False):
        super(Shreald, self).__init__(parent)
        self.cmd = cmd
        self.cwd = cwd
        self.mw = parent
        self.shell = shell
        self.daemon = True
        self.returncode = None
        self.log = []
        self.mw.showMessage("Shrealding %s " % (cmd))
        self.start()

#-------------------------------------------------------------------------------
# run()
#-------------------------------------------------------------------------------
    def run(self):
        if self.cmd:
            try:
                self.process = subprocess.Popen(self.cmd, cwd=self.cwd, bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell)
                ppid = psutil.Process(self.process.pid)
                self.mw.showMessage("Running shreald with PID %d" % (ppid.pid))
                q = queue.Queue()
                ti = threading.Thread(target=self.enqueueStream, args=(self.process.stdin, q, 0))
                to = threading.Thread(target=self.enqueueStream, args=(self.process.stdout, q, 1))
                te = threading.Thread(target=self.enqueueStream, args=(self.process.stderr, q, 2))
                tp = threading.Thread(target=self.enqueueProcess, args=(self.process, q))
                te.start()
                to.start()
                ti.start()
                tp.start()

                while True:
                    try:
                        line = q.get_nowait()
                        self.log.append(line)
                        self.linePrinted.emit(line)
                        if line[0] == 'x':
                            break
                    except:
                        pass

                tp.join()
                ti.join()
                to.join()
                te.join()
            except Exception as error:
                sError = traceback.format_exc()
                self.mw.showMessage("Shreald exception raised")
                self.mw.showMessage(sError)

#-------------------------------------------------------------------------------
# enqueueStream()
#-------------------------------------------------------------------------------
    def enqueueStream(self, stream, queue, type):
        # print("enqueue", flush=True)
        for line in iter(stream.readline, b''):
            queue.put(str(type) + line.decode(settings.db['SHELL_CODEPAGE']))
        stream.flush()
        stream.close()

#-------------------------------------------------------------------------------
# enqueueProcess()
#-------------------------------------------------------------------------------
    def enqueueProcess(self, process, queue):
        self.returncode = process.wait()
        # let's add some ignition delay to let time to complete the output
        time.sleep(0.3)
        queue.put('x')

#-------------------------------------------------------------------------------
# kill()
#-------------------------------------------------------------------------------
    def kill(self):
        ppid = psutil.Process(self.process.pid)
        for proc in ppid.children(recursive=True):
            proc.kill()
        ppid.kill()
