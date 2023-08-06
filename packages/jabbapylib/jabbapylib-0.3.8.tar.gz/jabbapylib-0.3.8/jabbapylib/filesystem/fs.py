#!/usr/bin/env python

"""
file system operations

# from jabbapylib.filesystem import fs
"""

import os
import sys
import stat
import json
import urlparse
from jabbapylib.dateandtime.dateandtime import get_timestamp_from_year_to_second

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']    # can be extended

BYTE = 1
KB = 1024 * BYTE
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB


def read_first_line(input_file):
    """Read the first line of a file.
    
    Useful to read username, password, etc.
    Security tip: store such files on a Truecrypt volume."""
    f = open(input_file, 'r')
    line = f.readline().rstrip('\n')
    f.close()
    
    return line


def is_local_path(path):
    """Decide if path is a local file. It can
    be a URL too. The path can point to
    a non-existing file too."""
    p = urlparse.urlparse(path)
    return (not p.scheme and not p.netloc)


def is_image_file(path):
    """Path can be a URL or local file. Decide
    if it's an image file or not."""
    path = path.lower()
    return any([path.endswith(x) for x in IMAGE_EXTENSIONS])


def get_timestamped_filename():
    """Return a timestamped text filename."""
    return '{ts}.txt'.format(ts=get_timestamp_from_year_to_second())


def remove_file_silently(fname):
    """Remove a file and don't complain if it doesn't exist.
    
    Return True if the file doesn't exist, otherwise return False."""
    try:
        os.unlink(fname)
    except:
        pass    # maybe it didn't exist
    
    return not os.path.exists(fname)


def touch(fname, mode=None):
    """Touch a file.
    
    If the file doesn't exist, it will be created. In this case
    you can specify its permissions.
    If the file exists, it will be touched. Permissions won't be changed.
    
    Return True if the file exists, otherwise return False.
    """
    # http://stackoverflow.com/questions/1158076/implement-touch-using-python
    if not os.path.exists(fname):
        open(fname, 'a').close()
        if mode:
            set_mode_to(fname, mode)
    else:
        os.utime(fname, None)
        
    return os.path.exists(fname)
        

def get_oct_mode(fname):
    """Get the permissions of an entry in octal mode.
    
    The return value is a string (ex. '0600')."""
    entry_stat = os.stat(fname)
    mode = oct(entry_stat[stat.ST_MODE] & 0777)
    return mode


def set_mode_to(fname, permissions):
    """Set the file with the given permissions.
    
    permissions is given as an octal number (not as a string), ex.: 0700 
    Return True if permissions were set successfully, otherwise return False."""
    mode = get_oct_mode(fname)
    if mode != oct(permissions):
        try:
            os.chmod(fname, permissions)
        except OSError:
            print >>sys.stderr, "# cannot chmod the file {0}".format(fname)
            
    return get_oct_mode(fname) == oct(permissions)


def store_content_in_file(content, file_name, overwrite=False, encode=None):
    """
    Store the content in a file.

    encode can be 'utf8' for instance
    """
    if os.path.exists(file_name) and not overwrite:
        print >>sys.stderr, "# warning: {0} exists.".format(file_name)
        return False
    # else
    try:
        f = open(file_name, 'w')
        if encode:
            f.write(content.encode(encode))
        else:
            f.write(content)
        f.close()
    except TypeError:
        print >>sys.stderr, "# warning: couldn't store {0}.".format(file_name)
        return False
    #
    return True


def which(program):
    """
    Equivalent of the which command in Python.
    
    source: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.split(program)[0]
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def read_json(fname):
    """Read an entire json file.
    
    Return value: the encoded Python object (list, dictionary, etc.)."""
    with open(fname, 'r') as f:
        return json.load(f)


def traverse(root, skip_links=True):
    """
    Traverse a directory recursively.

    Return all the items in the directory. Items are in absolute path.
    If skip_links is True, symbolic links are skipped.
    """
    entries = []
    return _traverse(os.path.abspath(root), entries, skip_links)


def _traverse(root, li, skip_links):
    """
    A helper function for traverse(). Don't call this directly,
    use it through traverse().
    """
    everything = [os.path.join(root, e) for e in os.listdir(root)]
    if skip_links:
        everything = [e for e in everything if not os.path.islink(e)]
    li += everything
    for d in [e for e in everything if os.path.isdir(e)]:
        _traverse(os.path.abspath(os.path.join(root, d)), li, skip_links)
    #
    return li


def sizeof_fmt(num):
    """
    Convert file size to human readable format.
    """
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "{0:.2f} {1}".format(num, x)
        num /= 1024.0

############################################################################# 
 
if __name__ == "__main__":
    #input_file = '/home/jabba/secret/project_euler/username.txt'
    #print read_first_line(input_file)
    #
#     path = 'http://google.com'
#     print is_local_path(path)
#     print get_timestamped_filename()
#     print get_oct_mode('/usr/bin/bash')
#     TMP = '/tmp/laci_20120119_tmp.txt'
#     touch(TMP, 0700)
#     print 'tmp:', get_oct_mode(TMP)
# #    set_mode_to(TMP, 0755)
# #    print 'tmp:', get_oct_mode(TMP)
#     print which('bash')
#     print is_image_file('/trash/hey.PNG')
    print sizeof_fmt(3980230656)