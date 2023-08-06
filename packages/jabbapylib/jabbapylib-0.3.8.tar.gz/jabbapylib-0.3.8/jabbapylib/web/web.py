#!/usr/bin/env python

"""
Working with webpages.
* download a page
* store a page (or image, etc.) in the file system

# from jabbapylib.web import web
# from jabbapylib.web.web import get_page
# from jabbapylib.web.web import get_page_with_cookies_using_cookiejar
"""

import os
import sys
import urllib
import urllib2
import urlparse
import tempfile
import webbrowser
import httplib    # status codes here: http://docs.python.org/library/httplib.html

from export_firefox_cookies import get_cookies_in_text, get_cookies_in_cookiejar
from jabbapylib.process import process
from jabbapylib import config as cfg
from jabbapylib.filesystem import fs
from jabbapylib.web.scraper import jabba_webkit as jw


class MyOpener(urllib.FancyURLopener):
    """Custom user-agent."""
    version = cfg.USER_AGENT
# MyOpener


def get_referer(url):
    """Get the referer of a URL.
    
    Ex.: http://example.com/dir/file.html => http://example.com,
    i.e. keep the protocol and the host.
    """
    p = urlparse.urlparse(url)
    return "{0}://{1}".format(p.scheme, p.netloc)
# get_referer


def get_host(url):
    """Get the host from a URL.
    
    Example: http://projecteuler.net/index.php?section=statistics => projecteuler.net"""
    p = urlparse.urlparse(url)
    return p.netloc


def get_url_open(url, user_agent=False, referer=False, timeout=None):
    """Open a URL.
    
    This is a helper function for others who want to read the URL.
    """
    req = urllib2.Request(url)
    if user_agent:
        req.add_header('User-Agent', MyOpener.version)
    if referer:
        req.add_header('Referer', get_referer(url))
    try:
        return urllib2.urlopen(req, timeout=timeout) if timeout else urllib2.urlopen(req)
    except:
        return None
# get_url_open


def get_url_info(url, user_agent=False, referer=False):
    """Get the meta-information of a page."""
    d = get_url_open(url, user_agent, referer)
    if d:
        result = d.info()
        d.close()
        return result
    # else
    return None
# get_url_info


def get_redirected_url(url):
    """Get the redirected URL.
    
    In case of problem, return None."""
    try:
        page = urllib.urlopen(url)
        return page.geturl()
    except:
        return None
# get_redirected_url


def get_server_status_code(url):
    """
    Download just the header of a URL and
    return the server's status code.
    """
    # http://stackoverflow.com/questions/1140661/python-get-http-response-code-from-a-url
    # in CLI: curl -I <url>
    host, path = urlparse.urlparse(url)[1:3]    # elems [1] and [2]
    try:
        conn = httplib.HTTPConnection(host)
        conn.request('HEAD', path)
        return conn.getresponse().status
    except StandardError:
        return None


def check_url(url):
    """
    Check if a URL exists without downloading the whole file.
    We only check the URL header.
    """
    # see also http://stackoverflow.com/questions/2924422 for further good codes
    # TODO: maybe the list of good codes should be extended
    good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]
    return get_server_status_code(url) in good_codes


def get_page(url, user_agent=True, referer=False, timeout=None):
    """Get the content of a page (HTML, image, etc.).
    
    Return value: string (can be binary too).
    """
    d = get_url_open(url, user_agent, referer, timeout)
    if d:
        result = d.read()
        d.close()
        return result
    # else
    return None
# get_page


def download_to(url, local_file, user_agent=False, referer=False, timeout=None, overwrite=False):
    """Fetch the content of a URL and store it in a local file."""
    content = get_page(url, user_agent=user_agent, referer=referer, timeout=timeout)
    fs.store_content_in_file(content, local_file, overwrite=overwrite)
# download_to


def get_page_with_cookies_using_wget(url):
    """Get the content of a cookies-protected page.
    
    The page is downloaded with wget. Cookies are passed to wget."""
    cookies = get_cookies_in_text(get_host(url))
    fs.store_content_in_file(cookies, cfg.COOKIES_TXT, overwrite=True)
    OPTIONS = "--cookies=on --load-cookies={0} --keep-session-cookies".format(cfg.COOKIES_TXT)
    cmd = "{wget} {options} '{url}' -qO-".format(wget=cfg.WGET, options=OPTIONS, url=url)
    page = process.get_simple_cmd_output(cmd)
    os.unlink(cfg.COOKIES_TXT)
    
    return page


def get_page_with_cookies_using_cookiejar(url, timeout=None):
    """Get the content of a cookies-protected page.
    
    The page is downloaded with urllib2. The cookies are passed in a cookiejar."""
    cj = get_cookies_in_cookiejar(get_host(url))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))      # cookies are added here
    urllib2.install_opener(opener)

    #txdata = None   # if we were making a POST type request, we could encode a dictionary of values here - using
    #params = {}
    #txdata = urllib.urlencode(params)
    #txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}          # fake a user agent, some websites (like google) don't like automated exploration
    #txheaders = {}
    #req = urllib2.Request(url, txdata, txheaders)            # create a request object

    req = urllib2.Request(url)
    # and open it to return a handle on the url
    handle = urllib2.urlopen(req, timeout=timeout) if timeout else urllib2.urlopen(req)

    return handle.read()


def get_js_page(url):
    """Get a page with Webkit, i.e. evaluate embedded JavaScripts."""
    return jw.get_page(url)

def open_in_browser(html, test=False):
    """Save an HTML source to a temp. file and open it in the browser.
    
    Return value: name of the temp. file."""
    temp = tempfile.NamedTemporaryFile(prefix='tmp', suffix='.html', dir='/tmp', delete=False)
    fs.store_content_in_file(html, temp.name, overwrite=True)
    if not test:
        webbrowser.open_new_tab(temp.name)
    return temp.name


def html_to_text(html, method=cfg.LYNX):
    """Convert an HTML source to text format. Two methods are available:
    (1) with lynx, (2) with html2text.py.
    
    The return value is a string.""" 
    temp = tempfile.NamedTemporaryFile(prefix='tmp', suffix='.html', dir='/tmp', delete=False)
    fs.store_content_in_file(html, temp.name, overwrite=True)
    if method == cfg.LYNX:
        cmd = "{lynx} {html} -dump".format(lynx=cfg.LYNX, html=temp.name)
    elif method == cfg.HTML2TEXT:
        cmd = "python {html2text} {html}".format(html2text=cfg.HTML2TEXT, html=temp.name)
    else:
        print >>sys.stderr, "Warning! Unknown method is used in web.html_to_text."
        os.unlink(temp.name)
        return None
    
    text = process.get_simple_cmd_output(cmd)
    os.unlink(temp.name)
    return text
    
#############################################################################

if __name__ == "__main__":
    #url = 'http://index.hu'
    #text = get_page(url)
    #print store_content_in_file(text, '/tmp/index.html', overwrite=True)
    url = 'http://projecteuler.net/progress'
    #print get_page_with_cookies_using_wget(url)

    # version 2
#    print get_page_with_cookies_using_cookiejar(url)
    
    # get JS page
#    url = 'http://simile.mit.edu/crowbar/test.html'
#    print get_js_page(url)

    print get_host(url)
    print urlparse.urlparse(url)
    url = '/media/truecrypt1/secret/tumblr/test_blog.txt'
    print urlparse.urlparse(url)
    #
    print '====='
    print get_server_status_code('http://simile.mit.edu/crowbar/test.html')
    
    print get_js_page('http://simile.mit.edu/crowbar/test.html')
    print '====='
    print get_js_page('http://simile.mit.edu/crowbar/test.html')
