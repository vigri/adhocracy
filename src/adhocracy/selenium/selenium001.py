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
#import multiprocessing
import time

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
                     date + " - Sourcecode.html": { "content": content },
                     date + " - Logfile.text": { "content": log }
                    }
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

        data = urllib.urlencode({ 'key' : apikey, 'image' : picture })
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
            log = open('logfile', 'r').read()
            if log == "":
                log = 'Error reading logfile'

        url = cls.gist_upload('Selenium driven test (' + cls.envSelectedBrowser + ')\n' + dt + '\n%r' % e + ']', cls.driver.page_source, log, dt)
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
        server_path = cls.script_dir + '/' + cls.getConfig('Selenium')['server']
        cmd = ['java', '-Djava.security.egd=file:/dev/./urandom', '-jar', server_path]
        cls.pSel_server = subprocess.Popen(cmd, stderr=null, stdout=null, preexec_fn=os.setsid)

    @classmethod
    def shutdown_selenium_server_standalone(cls):
        os.killpg(cls.pSel_server.pid, signal.SIGTERM)

    @classmethod
    def start_adhocracy(cls):
        cls.adhocracy_logfile = open('logfile', 'w')
        
        errors = check_port_free([5001], opts_kill='pgid', opts_gracePeriod=10)
        if errors:
            raise Exception("\n".join(errors))

        cls.pAdhocracy_server = subprocess.Popen(cls.adhocracy_dir + 'bin/adhocracy_interactive.sh', stderr=cls.adhocracy_logfile, stdout=cls.adhocracy_logfile, shell=True, preexec_fn=os.setsid)

        errors = check_port_free([5001], opts_gracePeriod=30, opts_graceInterval=0.1, opts_open=True)
        if errors:
            raise Exception("\n".join(errors))

    @classmethod
    def shutdown_adhocracy(cls):
        os.killpg(cls.pAdhocracy_server.pid, signal.SIGTERM)

    #### database-isolation functions
    @classmethod
    def _database_backup_create(cls):
        # Database isolation - trivial - copy database to some other destination
        shutil.copyfile(os.path.join(cls.adhocracy_dir, 'var', 'development.db'), os.path.join(cls.adhocracy_dir, 'src', 'adhocracy', 'selenium', 'bak_db', 'adhocracy_backup.db'))

    @classmethod
    def _database_backup_restore(cls):
        # Database isolation - trivial - restore our saved database
        shutil.copyfile(os.path.join(cls.adhocracy_dir, 'src', 'adhocracy', 'selenium', 'bak_db', 'adhocracy_backup.db'), os.path.join(cls.adhocracy_dir, 'var', 'development.db'))

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
        cls.pXvfb = subprocess.Popen(['Xvfb', ':' + str(display_number), '-ac', '-screen', '0', '1024x768x16'], stderr=null, stdout=null)

        # make a backup of the old DISPLAY-var
        cls.old_display = os.environ["DISPLAY"]
        cls.new_display = str(display_number)

        os.environ["DISPLAY"] = ":" + str(display_number)

    @classmethod
    def _remove_xvfb_display(cls):
        cls.pXvfb.kill()
        # restore the old DISPLAY-var
        os.environ["DISPLAY"] = cls.old_display

    @classmethod
    def _create_video(cls):
        # to get a better quality, decrease the qmax parameter

        null = open('/dev/null', 'wb')

        creationTime = int(time.time())
        cls.video_path = '/tmp/seleniumTest_' + str(creationTime) + '.mpg'
        cls.pFfmpeg = subprocess.Popen(['ffmpeg', '-f', 'x11grab', '-r', '25', '-s', '1024x768', '-qmax', '10', '-i', ':' + cls.new_display + '.0', cls.video_path], stderr=null, stdout=null)

    @classmethod
    def _stop_video(cls):
        cls.pFfmpeg.kill()

    #### global setUpClass and tearDownClass, + setUp, tearDown for each function
    @classmethod
    def setUpClass(cls):
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

        # Login / password for admin and non-user
        cls.adhocracy_login_admin = {'username': 'admin', 'password': 'password'}
        cls.adhocracy_login_user = {'username': '', 'password': ''}    # will be filled out by _create_default_user

        cls.defaultUser = ''
        cls.defaultUserPassword = ''
        cls.defaultProposalUrl = ''

        ##### Process environment variables

        # disable Xvfb
        cls.envShowTests = os.environ.get('selShowTests', '') == '1'

        # create video
        cls.envCreateVideo = os.environ.get('selCreateVideo', '') == '1'

        # selected browser
        try:
            cls.envSelectedBrowser = os.environ['selBrowser']
        except KeyError:
            cls.envSelectedBrowser = 'chrome'

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
        cls._create_webdriver(browser=cls.envSelectedBrowser)

        cls._create_default_user()

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

        # htmlunit needs a selenium server. If HU has been used, shutdown the server now
        if cls.envSelectedBrowser == 'htmlunit':
            cls.shutdown_selenium_server_standalone()

        # if we have started the adhocracy server, we are going to shut it down now
        if cls.envStartAdh:
            cls.shutdown_adhocracy()
            cls._database_backup_restore()

        # check if Xvfb has been used, if so, kill the process
        if not cls.envShowTests:
            cls._remove_xvfb_display()

        # if we've recorded a video, we'll stop the recording now
        if cls.envCreateVideo:
            cls._stop_video()
            print('  > Video record available: ' + cls.video_path)

            # now check if the user wants the video to be uploaded on youtube
            envYoutubeUpload = os.environ.get('envYoutubeUpload', '') == '1'
            if envYoutubeUpload:
                print('  > Uploading video, please wait...')
                desc = 'Selenium driven test using ' + cls.envSelectedBrowser
                title = 'Selenium ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                output = subprocess.Popen(['python', 'misc/youtube_upload.py', '--email=' + cls.getConfig('Youtube')['email'], '--password=' + cls.getConfig('Youtube')['password'], '--title="' + title + '"', '--description="' + desc + '"', '--category=Tech', '--keywords=Selenium', cls.video_path], stdout=subprocess.PIPE).communicate()[0]
                print ('  > ' + output)

    def setUp(self):
        if not self.setup_done:
            raise Exception('Global setup has not been called. Please use Python >=2.7 or nosetests')

    #### helper functions
    @classmethod
    def _create_default_user(cls):
        # This function creates a default user which can be used for other interactions within tests
        creationTime = int(time.time())
        userName = str(creationTime) + cls.envSelectedBrowser
        cls.loadPage('/register')

        i_username = cls.waitCSS('form[name="create_user"] input[name="user_name"]')
        i_username.send_keys(userName)

        i_email = cls.waitCSS('form[name="create_user"] input[name="email"]')
        i_email.send_keys(userName + '@example.com')

        i_password = cls.waitCSS('form[name="create_user"] input[name="password"]')
        i_password.send_keys('test')

        i_password2 = cls.waitCSS('form[name="create_user"] input[name="password_confirm"]')
        i_password2.send_keys('test')

        b_submit = cls.waitCSS('form[name="create_user"] input[type="submit"]')
        b_submit.click()

        cls.waitCSS('#user_menu')
        cls.force_logout()
        cls.adhocracy_login_user['username'] = userName
        cls.adhocracy_login_user['password'] = 'test'

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
                    cls.adhocracy_login = {'username': cls.adhocracy_login_admin['username'], 'password': cls.adhocracy_login_admin['password'], 'admin': True}
                else:
                    cls.adhocracy_login = {'username': cls.adhocracy_login_user['username'], 'password': cls.adhocracy_login_user['password'], 'admin': False}
                cls._login_user()
        else:
            if login_as_admin:
                cls.adhocracy_login = {'username': cls.adhocracy_login_admin['username'], 'password': cls.adhocracy_login_admin['password'], 'admin': True}
            else:
                cls.adhocracy_login = {'username': cls.adhocracy_login_user['username'], 'password': cls.adhocracy_login_user['password'], 'admin': False}
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

    def execute_js(self,js):
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
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
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

            cls.driver = webdriver.Remote(command_executor = 'http://127.0.0.1:4444/wd/hub', desired_capabilities = desired_caps)
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
            if cls.check_firefox_version():
                # everything okay
                cls.driver = webdriver.Firefox(firefox_profile=fp)
            else:
                # check env. var
                useFirefoxBin = os.environ.get('selUseFirefoxBin', '') == '1'
                if not useFirefoxBin:   # TODO Logic wrong!!!
                    ffbin = webdriver.firefox.firefox_binary.FirefoxBinary(cls.script_dir + '/' + cls.getConfig('Selenium')['firefox'])
                    cls.driver = webdriver.Firefox(firefox_profile=fp, firefox_binary=ffbin)
                else:
                    # installed version of firefox not found or too old.
                    # user didn't set the env. var... we will stop here.
                    raise Exception('Installed firefox version not found or too old. You may use the env. var. "selUseFirefoxBin" to use a firefox binary specified in selenium.ini')
        elif browser == 'chrome':
            cls.driver = webdriver.Chrome(cls.script_dir + '/' + cls.getConfig('Selenium')['chrome'])
            # No javascript-disable support for chrome!
        else:
            raise Exception('Invalid browser selected: ' + browser)

    @classmethod
    def check_firefox_version(cls):
        # checks if firefox version is older than 3.6
        try:
            output = subprocess.Popen(['firefox', '--version'], stdout=subprocess.PIPE).communicate()[0]
        except Exception as e:
            return False
        try:
            major, minor = map(int, re.search(r"(\d+).(\d+)", output).groups())
        except Exception as e:
            return False
        if (major, minor) < (3, 6):
            return False
        return True
if __name__ == '__main__':
    unittest.main()
