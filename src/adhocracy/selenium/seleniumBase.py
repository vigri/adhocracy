#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import shutil
import subprocess
import shlex
import os
import signal
import errno
import re
import httplib
import urllib
import urllib2
import json
import datetime
import base64
import ConfigParser
import signal
import sys
import time
import inspect
import tempfile
import socket
import struct
import fcntl

pth = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
script_folder = os.path.join(pth, '..', '..', '..', 'scripts')
misc_folder = os.path.join(pth, 'misc')

if script_folder not in sys.path:
    sys.path.insert(0, script_folder)

if misc_folder not in sys.path:
    sys.path.insert(0, misc_folder)

from check_port_free import check_port_free
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from ElementNotFound import ElementNotFound
from selenium.common.exceptions import TimeoutException


class selTest(unittest.TestCase):
    #### Decorators
    @classmethod
    def additionalInfoOnException(cls, func):
        def wrapper(cls):
            try:
                func(cls)
            except BaseException as e:
                cls._displayInformation(e)
                raise
        wrapper.__name__ = func.__name__
        return wrapper

    @classmethod
    def jsRequired(cls, func):
        def wrapper(cls):
            try:
                cls.driver.execute_script('return 0;')
            except Exception as e:
                #print('\n  > Exception: %r' % e)
                error_text = 'This function requires JavaScript'
                print('\n  > Exception: ' + error_text)
                raise Exception(error_text)
            func(cls)
        wrapper.__name__ = func.__name__
        return wrapper

    #### upload functions
    @classmethod
    def gist_upload(cls, desc, content, log, date):
        d = json.dumps({
            "description": desc,
            "public": False,
            "files": {
                    date + " - Sourcecode.html": {"content": content},
                    date + " - Logfile.text": {"content": log}}
        })
        res = urllib2.urlopen('https://api.github.com/gists', d).read()
        resd = json.loads(res)
        return resd['html_url']

    @classmethod
    def imgur_upload(cls, picture):
        #Imgur vars
        clientId = cls.getConfig('Imgur')['clientid']
        url = cls.getConfig('Imgur')['url']
        apikey = cls.getConfig('Imgur')['apikey']

        data = urllib.urlencode({'key': apikey, 'image': picture})
        req = urllib2.Request(url, data)
        req.add_header('Authorization', 'Client-ID ' + clientId)
        json_response = urllib2.urlopen(req)
        json_response = json.load(json_response)

        if(json_response['status'] == 200):
            return json_response['data']['link']
        else:
            return 'Error while uploading screenshot'

    @classmethod
    def _displayInformation(cls, e):
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not cls.envStartAdh:
            log = 'No logfile available. Existing adhocracy server was used'
        else:
            cls.adhocracy_logfile.flush()
            log = open(os.path.join('log', 'adhocracy'), 'r').read()
            if log == "":
                log = 'Error reading logfile'

        url = cls.gist_upload(
                            'Selenium driven test (' + cls.envSelectedBrowser + ')\n' + dt + '\n%r' % e + ']',
                            cls.driver.page_source,
                            log,
                            dt)
        print('\n  > Exception: %r' % e)
        print('  > Browser: ' + cls.envSelectedBrowser)
        print('  > Logfile and HTML sourcecode: ' + url)

        """ Since some drivers have no screenshot-support (such htmlunit) the image upload only can be performed
            if the screenshot function is supported
        """
        try:
            print('  > Screenshot: ' + cls.imgur_upload(cls.driver.get_screenshot_as_base64()))
        except Exception:
            print('  > Screenshot: not supported')

    #### search-functions
    @classmethod
    def waitCSS(cls, css, wait=10, raiseException=True):
        # the raiseException parameter is needed for functions which handle exceptions on their own
        if raiseException:
            try:
                func = lambda driver: driver.find_element_by_css_selector(css)
                WebDriverWait(cls.driver, wait).until(func, css)
                return func(cls.driver)
            except TimeoutException:
                raise ElementNotFound(css)

        else:
            func = lambda driver: driver.find_element_by_css_selector(css)
            WebDriverWait(cls.driver, wait).until(func, css)
            return func(cls.driver)

    @classmethod
    def waitXpath(cls, xpath, wait=10, raiseException=True):
        if raiseException:
            try:
                func = lambda driver: driver.find_element_by_xpath(xpath)
                WebDriverWait(cls.driver, wait).until(func)
                return func(cls.driver)
            except TimeoutException:
                raise ElementNotFound(xpath)
        else:
            func = lambda driver: driver.find_element_by_xpath(xpath)
            WebDriverWait(cls.driver, wait).until(func)
            return func(cls.driver)

    #### start / shutdown functions (adhocracy, selenium etc.)
    @classmethod
    def start_selenium_server_standalone(cls):
        null = open('/dev/null', 'wb')
        server_path = os.path.join(cls.script_dir, cls.getConfig('Selenium')['server'])
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-jar', server_path]
        cls.pSel_server = subprocess.Popen(cmd,
                                           stderr=null,
                                           stdout=null,
                                           preexec_fn=os.setsid)

        # Write PID file
        pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.pSel_server.pid) + '.pid')
        pidfile = open(pidfilename, 'wb')
        pidfile.write(str(cls.pSel_server.pid))
        pidfile.close()

    @classmethod
    def shutdown_selenium_server_standalone(cls):
        if hasattr(cls, 'pSel_server'):
            pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.pSel_server.pid) + '.pid')

            os.killpg(cls.pSel_server.pid, signal.SIGTERM)

            # remove pidfile
            if os.path.isfile(pidfilename):
                os.remove(pidfilename)

    @classmethod
    def start_adhocracy(cls):
        cls.adhocracy_logfile = open(os.path.join('log', 'adhocracy'), 'w+')

        errors = check_port_free([5001], opts_kill='pgid', opts_gracePeriod=10)
        if errors:
            raise Exception("\n".join(errors))

        cmd = cls.adhocracy_dir + os.path.join('bin', 'adhocracy_interactive.sh')

        cls.pAdhocracy_server = subprocess.Popen(cmd,
                                                 stderr=cls.adhocracy_logfile,
                                                 stdout=cls.adhocracy_logfile,
                                                 preexec_fn=os.setsid)

        errors = check_port_free([5001], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
        if errors:
            raise Exception("\n".join(errors))

        # Write PID file
        pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.pAdhocracy_server.pid) + '.pid')
        pidfile = open(pidfilename, 'wb')
        pidfile.write(str(cls.pAdhocracy_server.pid))
        pidfile.close()

    @classmethod
    def shutdown_adhocracy(cls):
        if hasattr(cls, 'pAdhocracy_server'):
            pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.pAdhocracy_server.pid) + '.pid')

            os.killpg(cls.pAdhocracy_server.pid, signal.SIGTERM)

            # remove pidfile
            if os.path.isfile(pidfilename):
                os.remove(pidfilename)
            return True
        else:
            return False

    #### database-isolation functions
    @classmethod
    def _database_backup_create(cls):
        # Database isolation - trivial - copy database to some other destination
        backup = os.path.join(cls.adhocracy_dir, 'src', 'adhocracy', 'selenium', 'tmp', 'adhocracy_backup.db')
        db = os.path.join(cls.adhocracy_dir, 'var', 'development.db')
        shutil.copyfile(db, backup)

    @classmethod
    def _database_backup_restore(cls):
        # Database isolation - trivial - restore our saved database
        backup = os.path.join(cls.adhocracy_dir, 'src', 'adhocracy', 'selenium', 'tmp', 'adhocracy_backup.db')
        db = os.path.join(cls.adhocracy_dir, 'var', 'development.db')
        shutil.copyfile(backup, db)

        #now we'll remove the backup file
        os.remove(backup)

    #### xvfb and video-record functions
    @classmethod
    def _create_xvfb_display(cls):
        # Used for xvfb output. For debugging purposes this can be set to a file
        null = open('/dev/null', 'wb')

        # Get virtual display
        # get first free virtual display number
        display_number = 0
        while True:
            display_number += 1
            if not os.path.isfile('/tmp/.X' + str(display_number) + '-lock'):
                break

        cmd = ['Xvfb',
               ':' + str(display_number),
               '-ac',
               '-screen',
               '0',
               '1024x768x16']

        cls.pXvfb = subprocess.Popen(cmd, stderr=null, stdout=null)

        # make a backup of the old DISPLAY-var
        cls.old_display = os.environ.get('DISPLAY', '0')
        cls.new_display = str(display_number)

        os.environ["DISPLAY"] = ":" + str(display_number)

        # Write PID file
        pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.pXvfb.pid) + '.pid')
        pidfile = open(pidfilename, 'wb')
        pidfile.write(str(cls.pXvfb.pid))
        pidfile.close()

    @classmethod
    def _remove_xvfb_display(cls):
        if hasattr(cls, 'pXvfb'):
            pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.pXvfb.pid) + '.pid')

            cls.pXvfb.kill()
            # restore the old DISPLAY-var
            os.environ["DISPLAY"] = cls.old_display

            # remove pid file
            if os.path.isfile(pidfilename):
                os.remove(pidfilename)

    @classmethod
    def _create_video(cls):
        # to get a better quality, decrease the qmax parameter

        nullout = open('/dev/null', 'wb')
        nullin = open('/dev/null', 'rb')

        creationTime = int(time.time())

        tmpfile = tempfile.mkstemp('.mpg', 'seleniumVideo_', '/tmp')
        cls.video_path = tmpfile[1]

        cmd = ['ffmpeg',
               '-f', 'x11grab',
               '-r', '25',
               '-s', '1024x768',
               '-i', ':' + cls.new_display + '.0',
               '-y',
               '-qmax', '10',
               cls.video_path]

        cls.pFfmpeg = subprocess.Popen(cmd,
                                       stderr=subprocess.STDOUT,
                                       stdout=nullout,
                                       stdin=nullin)

        # Write PID file
        pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.pFfmpeg.pid) + '.pid')
        pidfile = open(pidfilename, 'wb')
        pidfile.write(str(cls.pFfmpeg.pid))
        pidfile.close()

    @classmethod
    def _stop_video(cls):
        if hasattr(cls, 'pFfmpeg'):
            pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.pFfmpeg.pid) + '.pid')

            cls.pFfmpeg.kill()

            # remove pid file
            if os.path.isfile(pidfilename):
                os.remove(pidfilename)

            return True
        else:
            return False

    #### global setUpClass and tearDownClass, + setUp, tearDown for each function
    @classmethod
    def setUpClass(cls):
        # Signal handlers
        signal.signal(signal.SIGINT, cls.cleanup)
        signal.signal(signal.SIGTERM, cls.cleanup)

        # with Python < 2.7 setUpClass() will not be executed, so this var will not be set to true
        # each test checks if this var has been set to true
        cls.setup_done = True

        # get configuration File
        cls.script_dir = os.path.dirname(os.path.realpath(__file__))
        config_path = cls.script_dir + '/selenium.ini'

        if not os.path.isfile(config_path):
            raise Exception('Configuration file selenium.ini not found!')
        cls.Config = ConfigParser.ConfigParser()
        cls.Config.read(config_path)

        # general vars
        cls.login_cookie = ''
        cls.adhocracy_logfile = None
        cls.adhocracy_dir = cls.getConfig('Adhocracy')['dir']
        cls.pidfolder = os.path.join(cls.script_dir, 'tmp')
        # Login / password for admin and non-user
        cls.adhocracy_login_admin = {'username': 'admin', 'password': 'password'}
        cls.adhocracy_login_user = {'username': '', 'password': ''}    # will be filled out by _create_default_user

        cls.defaultUser = ''
        cls.defaultUserPassword = ''
        cls.defaultProposalUrl = ''

        nullout = open('/dev/null', 'wb')
        # kill old processes which are created by this script and older than 24h
        cmd = os.path.join(cls.script_dir,'scripts','cleanup.py')
        cls.cleanup = subprocess.Popen(['python',cmd],stderr=nullout,stdout=nullout)

        if not os.path.exists('log'):
            os.makedirs('log')
        ##### Process environment variables

        # disable Xvfb
        cls.envShowTests = os.environ.get('selShowTests', '') == '1'

        # create video
        cls.envCreateVideo = os.environ.get('selCreateVideo', '') == '1'

        # selected browser
        cls.envSelectedBrowser = os.environ.get('selBrowser', 'chrome')

        # javascript
        cls.envDisableJs = os.environ.get('selDisableJS', '') == '1'

        # start local adhocracy server
        cls.envStartAdh = os.environ.get('selStartAdh', '') == '1'

        # remote adhocracy url
        try:
            cls.adhocracyUrl = os.environ['selAdhocracyUrl']
            cls.adhocracy_remote = True
            cls.envStartAdh = False
        except KeyError:
            cls.adhocracyUrl = 'http://adhocracy.lan:5001'
            cls.adhocracy_remote = False

        #### Take actions based on env. vars.

        # Since htmlunit has no real display output, envShowTests and envCreateVideo cannot be used
        if cls.envSelectedBrowser == 'htmlunit':
            cls.envShowTests = False
            cls.envCreateVideo = False

        if not cls.envShowTests:
            cls._create_xvfb_display()
        else:
            cls.envCreateVideo = False

        if cls.envCreateVideo:
            cls._create_video()

        # Start adhocracy server if specified
        if not cls.adhocracy_remote:
            if cls.envStartAdh:
                # create a backup of the actual database
                cls._database_backup_create()
                # Start Adhocracy
                cls.start_adhocracy()

        # create webdriver based on selected browser
        #cls._create_webdriver(browser=cls.envSelectedBrowser)
        cls._create_remote_webdriver(browser=cls.envSelectedBrowser, ops='linux')

        # check if adhocracy is online
        if not cls.check_adhocracy_online():
            cls.tearDownClass()
            raise Exception('Adhocracy-Website not available.')

        cls._create_default_user()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.close()

        # if chrome was used we need to kill chromedriver manually
        if hasattr(cls, 'chromedriverPid'):
            os.kill(cls.chromedriverPid, signal.SIGKILL)

            # remove pid file
            pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.chromedriverPid) + '.pid')
            if os.path.isfile(pidfilename):
                os.remove(pidfilename)

        # htmlunit needs a selenium server. If HU has been used, shutdown the server now
        if cls.envSelectedBrowser == 'htmlunit':
            cls.shutdown_selenium_server_standalone()

        # if we have started the adhocracy server, we are going to shut it down now
        if cls.envStartAdh:
            if cls.shutdown_adhocracy():
                cls._database_backup_restore()

        # check if Xvfb has been used, if so, kill the process
        if not cls.envShowTests:
            cls._remove_xvfb_display()

        ## kill cleanup process
        cls.cleanup.kill()

        # if we've recorded a video, we'll stop the recording now
        if cls.envCreateVideo:
            if cls._stop_video():
                print('  > Video record: ' + cls.video_path)

                # now check if the user wants the video to be uploaded on youtube
                envYoutubeUpload = os.environ.get('envYoutubeUpload', '') == '1'
                if envYoutubeUpload:
                    print('  > Uploading video, please wait...')
                    desc = 'Selenium driven test using ' + cls.envSelectedBrowser
                    title = 'Selenium ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    output = subprocess.Popen(['python', 'misc/youtube_upload.py',
                                               '--email=' + cls.getConfig('Youtube')['email'],
                                               '--password=' + cls.getConfig('Youtube')['password'],
                                               '--title="' + title + '"', '--description="' + desc + '"',
                                               '--category=Tech',
                                               '--keywords=Selenium',
                                               cls.video_path],
                                              stdout=subprocess.PIPE).communicate()[0]
                    print ('  > ' + output)

    def setUp(self):
        if not self.setup_done:
            raise Exception('Global setup has not been called. Please use Python >=2.7 or nosetests')

    #### helper functions
    @classmethod
    def _create_default_user(cls):
        # This function creates a default user which can be used for other interactions within tests
        # we do here our error handling, since without raiseException=False tearDownClass will not be called

        creationTime = int(time.time())
        userName = str(creationTime) + cls.envSelectedBrowser

        try:
            cls.loadPage('/register')
            i_username = cls.waitCSS('form[name="create_user"] input[name="user_name"]', raiseException=False)
            i_username.send_keys(userName)

            email = cls.waitCSS('form[name="create_user"] input[name="email"]', raiseException=False)
            email.send_keys(userName + '@example.com')

            pwd = cls.waitCSS('form[name="create_user"] input[name="password"]', raiseException=False)
            pwd.send_keys('test')

            pwd2 = cls.waitCSS('form[name="create_user"] input[name="password_confirm"]', raiseException=False)
            pwd2.send_keys('test')

            submit = cls.waitCSS('form[name="create_user"] input[type="submit"]', raiseException=False)
            submit.click()

            cls.waitCSS('#user_menu', raiseException=False)
            cls.force_logout()
            cls.adhocracy_login_user['username'] = userName
            cls.adhocracy_login_user['password'] = 'test'
        except TimeoutException:
            print('  > Error creating default user')
            cls.tearDownClass()
            sys.exit(0)

    #### Login functions
    @classmethod
    def _login_user(cls):
        cls.loadPage()

        l_login = cls.waitCSS('#nav_login > a')
        l_login.click()

        i_login = cls.waitCSS('input[name="login"]')
        i_login.send_keys(cls.adhocracy_login['username'])

        i_password = cls.waitCSS('input[name="password"]')
        i_password.send_keys(cls.adhocracy_login['password'])

        b_submit = cls.waitCSS('form[name="login"] input[type="submit"]')
        b_submit.click()

        cls.waitCSS('#user_menu')

        cls.cookies = cls.driver.get_cookies()
        for cookie in cls.cookies:
            if cookie['name'] == 'adhocracy_login':
                cls.login_cookie = cookie

    @classmethod
    def ensure_login(cls, login_as_admin=False):
        # check if the user is currently logged in
        if cls.login_cookie:
            # only do something if the current login-type differs from the desired login-type
            if cls.adhocracy_login['admin'] != login_as_admin:
                # delete the stored cookie-var and relevant cookie
                cls.force_logout()

                if login_as_admin:
                    cls.adhocracy_login = {'username': cls.adhocracy_login_admin['username'],
                                           'password': cls.adhocracy_login_admin['password'],
                                           'admin': True}
                else:
                    cls.adhocracy_login = {'username': cls.adhocracy_login_user['username'],
                                           'password': cls.adhocracy_login_user['password'],
                                           'admin': False}
                cls._login_user()
        else:
            if login_as_admin:
                cls.adhocracy_login = {'username': cls.adhocracy_login_admin['username'],
                                       'password': cls.adhocracy_login_admin['password'],
                                       'admin': True}
            else:
                cls.adhocracy_login = {'username': cls.adhocracy_login_user['username'],
                                       'password': cls.adhocracy_login_user['password'],
                                       'admin': False}
            cls._login_user()

    @classmethod
    def force_logout(cls):
        # Delete the login-cookie (if existent) to ensure the user is not logged in
        cls.login_cookie = ''
        cls.driver.delete_cookie('adhocracy_login')

    #### misc functions
    def ensure_is_member_of_group(self):
        # Check if the user needs to join the instance, if so, click on the 'join' button
        # if an timeoutException occurs, it means, we are allready a member and don't need to join
        # raiseException is set to False, so nothing happens if the 'join' button is not found
        try:
            b_join_group = self.waitCSS('.message .register > a', wait=2, raiseException=False)
            b_join_group.click()
        except TimeoutException:
            pass

    def make_element_visible_by_id(self, elementId):
        self.execute_js('document.getElementById("' + elementId + '").style.display = "block";')

    def execute_js(self, js):
        try:
            return self.driver.execute_script(js)
        except Exception:
            raise Exception('Error executing JavaScript')

    @classmethod
    def getConfig(cls, section):
        #http://wiki.python.org/moin/ConfigParserExamples
        dict1 = {}
        options = cls.Config.options(section)
        for option in options:
            try:
                dict1[option] = cls.Config.get(section, option)
                if dict1[option] == -1:
                    print('exception on %s!' % option)
            except:
                print('exception on %s!' % option)
                dict1[option] = None
        return dict1

    @classmethod
    def loadPage(cls, path=''):
        cls.driver.get(cls.adhocracyUrl + path)

    @classmethod
    def _create_webdriver(cls, browser):
        if browser == 'htmlunit':
            errors = check_port_free([4444], opts_kill='pgid', opts_gracePeriod=10)
            if errors:
                raise Exception("\n".join(errors))

            # Start Selenium Server Standalone
            cls.start_selenium_server_standalone()

            errors = check_port_free([4444], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
            if errors:
                raise Exception("\n".join(errors))

            desired_caps = webdriver.DesiredCapabilities.HTMLUNIT
            desired_caps['version'] = '2'

            if(cls.envDisableJs):
                desired_caps['javascriptEnabled'] = 'False'
            else:
                desired_caps['javascriptEnabled'] = 'True'

            cls.driver = webdriver.Remote(command_executor='http://127.0.0.1:4444/wd/hub', desired_capabilities=desired_caps)
        elif browser == 'firefox':
            fp = webdriver.FirefoxProfile()

            if(cls.envDisableJs):
                fp.set_preference('javascript.enabled', False)

            """
              Firefox >= 3.6 is needed for using selenium webdriver.
              first we check if the installed version is okay
              if not, we check if the user set the env. var. selUseFirefoxBin which will
              use the firefox binary specified in selenium.ini
            """

            useFirefoxBin = os.environ.get('selUseFirefoxBin', '') == '1'

            if useFirefoxBin:
                firefoxBinary = os.path.join(cls.script_dir, cls.getConfig('Selenium')['firefox'])
                ffbin = webdriver.firefox.firefox_binary.FirefoxBinary(firefoxBinary)
                cls.driver = webdriver.Firefox(firefox_profile=fp, firefox_binary=ffbin)
            else:
                if cls.check_firefox_version():
                    # everything okay
                    cls.driver = webdriver.Firefox(firefox_profile=fp)
                else:
                    # installed version of firefox not found or too old.
                    # user didn't set the env. var... we will stop here.
                    cls.tearDownClass()
                    raise Exception('Installed firefox version not found or too old. You may use the env. var. "selUseFirefoxBin" to use a firefox binary specified in selenium.ini')

        elif browser == 'chrome':
            if cls.check_chrome_version():
                cls.driver = webdriver.Chrome(
                                            os.path.join(cls.script_dir, cls.getConfig('Selenium')['chrome']),
                                            service_log_path=os.path.join('log', 'chromedriver'))
                # since chromedriver will not be closed even if we call cls.driver.close()
                # we need to store the PID of chromedriver and kill it inside tearDownClass()
                cls.chromedriverPid = cls.driver.service.process.pid

                # Write PID file
                pidfilename = os.path.join(cls.pidfolder, 'selenium_' + str(cls.chromedriverPid) + '.pid')
                pidfile = open(pidfilename, 'wb')
                pidfile.write(str(cls.chromedriverPid))
                pidfile.close()

                # No javascript-disable support for chrome!
            else:
                cls.tearDownClass()
                raise Exception('Google-Chrome not found or too old. Please install Google-Chrome >= 24.0')
        else:
            raise Exception('Invalid browser specified: ' + browser)

    @classmethod
    def _create_remote_webdriver(cls, browser, ops):
        # Select the desired browser based on config file    TODO: default case
        if browser == "htmlunit":
            desired_caps = webdriver.DesiredCapabilities.HTMLUNIT
            desired_caps['version'] = "2"
        elif browser == "firefox":
            desired_caps = webdriver.DesiredCapabilities.FIREFOX
        elif browser == "chrome":
            desired_caps = webdriver.DesiredCapabilities.CHROME
        elif browser == "internetexplorer":
            desired_caps = webdriver.DesiredCapabilities.INTERNETEXPLORER
        else:
            raise Exception('Invalid browser selected: ' + browser)
        
        hosts = cls.getP2PHosts()
        #print hosts
        # get first host which matches the desired browser and operating system
        for host in hosts:
            if host[2]  == ops and host[3] == browser:
                cls.driver = webdriver.Remote(
                    command_executor = 'http://' + host[0] + ':' + host[1] + '/wd/hub',
                    desired_capabilities=desired_caps
                )
                #print('DEBUG: Text will be executed on ' + command_executor)

                # the adhocracyUrl needs to be a IP adress which can be reached through lan
                # so adhocracy.lan:5001 might not work and 127.0.0.1:5001 can't be used.
                # using the local ip instead
                interface = cls.getConfig('P2P')['interface']
                ip = cls.get_ip(interface)
                if ip == "":
                    raise Exception('IP address from ' + interface + ' could not be resolved')
                else:
                    print(' DEBUG: Using IP: ' + ip)
                    cls.adhocracyUrl = 'http://' + ip + ':5001'
                    return

        if not hasattr(cls, 'driver'):
            raise Exception('No proper host found for browser = ' + browser + ' and os = ' + ops)

    @classmethod
    def check_firefox_version(cls):
        # checks if firefox version is older than 3.6
        try:
            output = subprocess.Popen(['firefox', '--version'],
                                      stdout=subprocess.PIPE
                                      ).communicate()[0]
            major, minor = map(int, re.search(r"(\d+).(\d+)", output).groups())
            return (major, minor) >= (3, 6)
        except Exception:
            return False

    @classmethod
    def check_chrome_version(cls):
        # checks if google-chrome is older than 24.0
        # note: chromium 6 does not work with selenium!
        try:
            output = subprocess.Popen(['google-chrome', '--version'],
                                      stdout=subprocess.PIPE
                                      ).communicate()[0]
            major, minor = map(int, re.search(r"(\d+).(\d+)", output).groups())
            return (major, minor) >= (24, 0)
        except Exception:
            return False

    @classmethod
    def getP2PHosts(cls):
        # search for selenium servers using bonjour
        hosts=[]

        if not os.path.exists("/usr/bin/avahi-browse"):
            raise Exception('Avahi-browse not found')
        client_list=subprocess.Popen(["avahi-browse","-trp","_selenium._tcp"],stdout=subprocess.PIPE)
        client_list.wait()
        for line in client_list.stdout.readlines():
            if line.startswith("="):
                try:
                    dat=line.split(";")
                    if len(dat) == 10:
                        if dat[2] == "IPv4":
                            tmp = []
                            tmp.append(dat[7]) # ip
                            tmp.append(dat[8])
                            # txt_record
                            txt_record = dat[9][1:-2]
                            txt_data = txt_record.split('" "')
                            browser = txt_data[0].partition('=')[2]
                            ops = txt_data[1].partition('=')[2]

                            tmp.append(ops) # operating system (windows|linux)
                            tmp.append(browser)
                            hosts.append(tmp)
                except:
                    pass
        return hosts

    @classmethod
    def get_ip(cls, iface = 'eth0'):
        # http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockfd = sock.fileno()
        SIOCGIFADDR = 0x8915

        ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00'*14)
        try:
            res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
        except:
            return ""
        ip = struct.unpack('16sH2x4s8x', res)[2]
        return socket.inet_ntoa(ip)

    @classmethod
    def check_adhocracy_online(cls):
        try:
            status =  urllib.urlopen(cls.adhocracyUrl).getcode()
            if status == 200:
                return True
            else:
                return False
        except IOError:
            return False

    @classmethod
    def cleanup(cls, signal, frame):
        # will be called with SIGINT, SIGTERM
        cls.tearDownClass()
        sys.exit(0)

if __name__ == '__main__':
    unittest.main()
