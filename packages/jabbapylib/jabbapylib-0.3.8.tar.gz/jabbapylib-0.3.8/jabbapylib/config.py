#!/usr/bin/env python

"""
Configuration part.

# from jabbapylib import config as cfg
"""

__author__ = "Laszlo Szathmary (jabba.laci@gmail.com)"
__version__ = "0.3.8"
__date__ = "20130413"
__copyright__ = "Copyright (c) 2011-2013 Laszlo Szathmary"
__license__ = "GPL"

import os

# portability tip: in ~/.mozilla/firefox put a symbolic link on 
# ~/.mozilla/firefox/XXXXXXXX.default/cookies.sqlite
COOKIE_DB = "{home}/.mozilla/firefox/cookies.sqlite".format(home=os.path.expanduser('~'))
ESPEAK = '/usr/bin/espeak'
MPLAYER = '/usr/bin/mplayer'
WGET = '/usr/bin/wget'
XSEL = '/usr/bin/xsel'
TIDY = '/usr/bin/tidy'
LYNX = '/usr/bin/lynx'
TESSERACT2 = '/usr/bin/tesseract'    # tesseract 2, installed via apt-get
TESSERACT3 = '/usr/local/bin/tesseract'    # tesseract 3, install notes: 
# (1) http://code.google.com/p/tesseract-ocr/wiki/ReadMe
# (2) http://ubuntuforums.org/showthread.php?t=1647350
MY_TESSERACT = TESSERACT3    # use this version
XRANDR = '/usr/bin/xrandr'
PRIMES = '/usr/games/primes' # sudo apt-get install bsdgames
FPING = '/usr/bin/fping'
XDOTOOL = '/usr/bin/xdotool'

required_files = (
    COOKIE_DB,      # to get webpages that are protected with cookies
    ESPEAK,         # text to speech
    MPLAYER,        # play audio/video
    WGET,           # get webpages
    XSEL,           # copy to clipboard
    TIDY,           # tidy up HTML source
    LYNX,           # for converting HTML to text
    MY_TESSERACT,   # OCR
    XRANDR,         # screen resolution
    PRIMES,         # for generating prime numbers in an interval
    FPING,          # pings hosts, produces readable output
    XDOTOOL,        # xdotool, command-line X11 automation tool (get window ID, put focus on a window, etc.)
)

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0'
COOKIES_TXT = '{home}/tmp/cookies_jabbapylib_tmp.txt'.format(home=os.path.expanduser('~'))

ROOT_DIR = os.path.dirname(__file__)
TEST_ASSETS_DIR = os.path.dirname(__file__) + '/../tests/_assets'
TEST_TMP_DIR = os.path.dirname(__file__) + '/../tests/_tmp'
TEST_TMP_FILE = os.path.dirname(__file__) + '/../tests/_tmp/test.tmp'

TMP_DIR = '/tmp/jabbapylib_20120119_tmp'
TMP_FILE = '/tmp/jabbapylib_20120119_tmp.txt'

HTML2TEXT = os.path.dirname(__file__) + '/lib/html2text.py'

# an anonymous API key (find more at http://imgur.com/apps)
IMGUR_KEY = '014fd9069edf931bf1148b80da1cd09e'

#############################################################################

if __name__ == "__main__":
    print TEST_ASSETS_DIR
