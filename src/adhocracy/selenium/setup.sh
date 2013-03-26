#!/bin/bash 

# Install all relevant dependencies for using selenium with htmlunit, chrome, firefox
# and features like video recording, youtube-upload

echo "Installing xvfb, python-progressbar, python-pycur,l ia32-libs-gtk, ffmpeg..."
sudo apt-get -f install
sudo apt-get install xvfb python-progressbar python-pycurl ia32-libs-gtk ffmpeg -y -q

echo ""
echo "Getting Google Chrome..."
# check if user has a x64 or x86 system...
MACHINE_TYPE=`uname -m`
if [ ${MACHINE_TYPE} == 'x86_64' ]; then
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo dpkg -i google-chrome-stable_current_amd64.deb
else
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_i386.deb
  sudo dpkg -i google-chrome-stable_current_i386.deb
fi

rm *.deb

mkdir -p res

cd res
echo ""
echo "Getting Selenium server..."
mkdir -p selenium
cd selenium
rm -rf *
wget -q --output-document selenium-server-standalone.jar https://selenium.googlecode.com/files/selenium-server-standalone-2.31.0.jar
cd ..

echo "Getting Chromedriver..."
mkdir -p chrome
cd chrome
rm -rf *
wget -q https://chromedriver.googlecode.com/files/chromedriver_linux64_26.0.1383.0.zip
unzip -j -qq *.zip
rm *.zip
cd ..

echo "Getting Firefox..."
mkdir -p firefox
cd firefox
rm -rf *
cd ..
wget -q --output-document firefox.tar.bz2 http://download-origin.cdn.mozilla.net/pub/mozilla.org/firefox/releases/19.0.2/linux-x86_64/en-US/firefox-19.0.2.tar.bz2
tar xf firefox.tar.bz2
rm firefox.tar.bz2
cd ..

echo ""
echo "> Done..."


