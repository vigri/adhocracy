#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This script can be used as a cronjob to clean up
not needed processes (which are older than 24h) created by selenium tests.
Dead processes can occur if the test is suddenly aborted
and no tearDownClass() was called
"""
import os
import inspect
import sys

pth = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
script_folder = os.path.join(pth, '..', '..', '..', '..', 'scripts')

if script_folder not in sys.path:
    sys.path.insert(0, script_folder)

import subprocess
import glob
import time
import datetime
import signal

from genericpath import isdir, isfile
from check_port_free import check_port_free


def cleanup():
    tmp_folder = os.path.join(pth, '..', 'tmp')

    os.chdir(tmp_folder)
    for files in glob.glob('selenium_*'):
        pid_path = os.path.join(tmp_folder, files)
        file_ts = int(os.stat(pid_path).st_mtime)
        now = int(time.time())

        if file_ts < (now - 3600):
            # process is too old!
            # now we reed the pid
            content = open(pid_path).readlines()

            proc_path = os.path.join('/proc', str(content[0]), 'cmdline')
            if isfile(proc_path):
                # the pid still exists, we're going now to kill it

                try:
                    os.kill(int(content[0]), signal.SIGKILL)
                    print('Process killed: ' + content[0])
                    os.remove(pid_path)
                except Exception:
                    print('[ERROR] Proces not killed' + str(content[0]))
            else:
                # remove pid file
                print('Outdated pidfile removed ' + files)
                os.remove(pid_path)

if __name__ == '__main__':
    cleanup()
