#!/bin/bash 

# Install all relevant dependencies for using selenium additionally with htmlunit, firefox
# and features like video recording, youtube-upload

#http://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/`basename "${BASH_SOURCE[0]}"`
SCRIPT_FOLDER=`dirname $ABSOLUTE_PATH`
SELFOLDER=`dirname $SCRIPT_FOLDER`

PKGS_TO_INSTALL="xvfb python-progressbar python-pycurl ia32-libs-gtk ffmpeg avahi-utils"
echo "Installing $PKGS_TO_INSTALL"
sudo apt-get install $PKGS_TO_INSTALL -y -q

echo ""

# create folders
mkdir -p $SELFOLDER/res
mkdir -p $SELFOLDER/log
mkdir -p $SELFOLDER/tmp
mkdir -p $SELFOLDER/res/linux
mkdir -p $SELFOLDER/res/windows
mkdir -p $SELFOLDER/res/all

rm -rf $SELFOLDER/res/all/selenium
rm -rf $SELFOLDER/res/linux/firefox
rm -rf $SELFOLDER/res/linux/chrome

cd $SELFOLDER/res/all

echo ""
echo "Getting Selenium server..."
mkdir -p selenium
cd selenium
wget -nv -O selenium-server-standalone.jar https://selenium.googlecode.com/files/selenium-server-standalone-2.31.0.jar
cd ..

cd $SELFOLDER/res/linux

echo "Getting Firefox..."
wget -nv -O firefox.tar.bz2 http://download-origin.cdn.mozilla.net/pub/mozilla.org/firefox/releases/19.0.2/linux-x86_64/en-US/firefox-19.0.2.tar.bz2
tar xf firefox.tar.bz2
rm firefox.tar.bz2

echo "Getting chromedriver.."
mkdir -p chrome
cd chrome
# get chromedriver for selenium_node.py (p2p-testing) (even if may be located in /usr/local/bin)
if [ `getconf LONG_BIT` = "64" ]
then
    wget -nv -O chromedriver_linux https://chromedriver.googlecode.com/files/chromedriver_linux64_26.0.1383.0.zip
    
else
    wget -nv -O chromedriver_linux https://chromedriver.googlecode.com/files/chromedriver_linux32_26.0.1383.0.zip
fi

unzip -j -qq chromedriver_linux
rm chromedriver_linux


# get google chrome for selenium testing
if which google-chrome >/dev/null ; then
  echo "Google chrome installed... skipping..."
else
  echo "Installing google Chrome"
  if [ `getconf LONG_BIT` = "64" ]
  then
      wget -nv https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
      sudo dpkg -i google-chrome-stable_current_amd64.deb
      rm google-chrome-stable_current_amd64.deb
  else
      wget -nv https://dl.google.com/linux/direct/google-chrome-stable_current_i386.deb
      sudo dpkg -i google-chrome-stable_current_i386.deb
      rm google-chrome-stable_current_i386.deb
  fi
fi

echo ""
echo "> Done..."


