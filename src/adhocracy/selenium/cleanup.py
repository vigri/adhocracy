#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This script can be used as a cronjob to clean up
not needed processes (which are older than 24h) created by selenium tests.
Dead processes can occur if the test is suddenly aborted
and no tearDownClass() was called
"""

import subprocess


def cleanup(proc):
    null = open('/dev/null', 'wb')

    cmd = ['killall', '-r', '--older-than', '24h', proc]
    subprocess.call(cmd, shell=False, stderr=null, stdout=null)

proc_list = ['Xvfb', 'chrome', 'firefox', 'selenium']

while proc_list:
    cleanup(proc_list.pop())
