#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Run multiple browsertests simultaneously
    To add new browsers, simply extend browser_lists
"""

import subprocess
import os

from multiprocessing import Pool

# IMPORTANT:
# If you dont have firefox installed or your version is older than 3.6 you need to uncomment the following line
useFirefoxBinary = True


def start_test(browser):
    os.environ["selBrowser"] = browser
    script_folder = os.path.dirname(os.path.realpath(__file__))

    ff_env = os.environ.copy()

    if useFirefoxBinary == True:
        ff_env['selUseFirefoxBin'] = "True"

    cmd = ['nosetests', script_folder + '/../test_basic.py', '-sv']
    subprocess.call(cmd, shell=False, env=ff_env)

if __name__ == '__main__':
    browser_list = ['firefox', 'chrome', 'htmlunit']

    pool = Pool()
    while browser_list:
        pool.apply_async(start_test, [browser_list.pop()])
    pool.close()
    pool.join()
