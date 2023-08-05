#!/usr/bin/env python

"""
Automate your browser via telnet.
Requirements:
* Firefox
* MozRepl add-on (https://addons.mozilla.org/en-US/firefox/addon/mozrepl/)
  - activate the add-on ("Start" and "Activate on startup")

Documentation of gBrowser:
* https://developer.mozilla.org/en-US/docs/XUL/tabbrowser (reference)
* https://developer.mozilla.org/en-US/docs/Code_snippets/Tabbed_browser (code snippets)
"""

import re
import time
import sys
import  socket
import telnetlib

HOST = 'localhost'
PORT = 4242

prompt = [r'repl\d*> ']    # list of regular expressions

#"""
#based on https://github.com/bard/mozrepl/wiki/Pyrepl
#"""
class Mozrepl(object):
    def __init__(self, ip="127.0.0.1", port=4242):
        self.ip = ip
        self.port = port
        self.prompt = [r'repl\d*> ']    # list of regular expressions

    def __enter__(self):
        self.tn = telnetlib.Telnet(self.ip, self.port)
        self.tn.expect(prompt)
        return self

    def __exit__(self, type, value, traceback):
        self.tn.close()
        del self.tn

    def cmd(self, command):
        """
        Execute the command and don't fetch its result.
        """
        self.tn.write(command.encode() + b"\n")
        return self.tn.expect(self.prompt)

    def get_result(self, command):
        """
        Execute the command AND fetch its result.
        """
        lines = self.cmd(command).split("\n")
        if re.search(self.prompt[0].strip(), lines[-1]):
            lines = lines[:-1]
        return ''.join(lines)


def open_curr_tab(url):
    """
    Open a URL in the *current* tab.
    """
    with Mozrepl() as mr:
        cmd = "content.location.href = '{url}'".format(url=url)
        mr.cmd(cmd)


def open_new_empty_tab():
    """
    Open a new empty tab and put the focus on it.
    """
    with Mozrepl() as mr:
        mr.cmd('gBrowser.addTab()')
        mr.cmd('length = gBrowser.tabContainer.childNodes.length')
        mr.cmd('gBrowser.selectedTab = gBrowser.tabContainer.childNodes[length-1]')


def is_mozrepl_installed():
    """
    Test if MozRepl is installed.

    We simply try to connect to localhost:4242 where
    MozRepl should be listening.
    """
    try:
        with Mozrepl() as mr:
            pass
        return True
    except socket.error:
        return False


def close_curr_tab():
    """
    Close the current tab.
    """
    with Mozrepl() as mr:
        mr.cmd('gBrowser.removeCurrentTab()')

#############################################################################

if __name__ == "__main__":
    if not is_mozrepl_installed():
        print 'Cannot connect to localhost:4242.'
        print 'Make sure that the MozRepl Firefox add-on is installed and activated.'
        sys.exit(1)
    else:
#        sec = 4
#        print 'Demo'
#        #
#        print '* open a new tab'
#        open_new_empty_tab()
#        print '* wait {X} sec.'.format(X=sec)
#        time.sleep(sec)
#        #
#        print '* open python.org in current tab'
#        open_curr_tab('http://www.python.org')
#        print '* wait {X} sec.'.format(X=sec)
#        time.sleep(sec)
#        #
#        print '* close current tab'
#        close_curr_tab()
#        print '* done'
        close_curr_tab()
