#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###  
# Copyright (c) Rice University 2012
# This software is subject to
# the provisions of the GNU Lesser General
# Public License Version 2.1 (LGPL).
# See LICENCE.txt for details.
###

"""

given a source directory, assume it is .git, assume it is not faulty,
get a git-describe and the current branch and return a valid version

If it is not a git directory, look for RELEASE_VERSION file
that holds a songle line.  Use that.

If RELEASE_VERSION and git not exists - throw out a date, and hope.


Hacked up a state machine here cos it got a little too complex.

get_version
  flag = "START"
  - calls get_gitdescribe(coderoot, flag)
    returns ("NOGITTAG", None) 
            ("YESGITTAG", "1.0.0")
  Then
  - calls get_versionfile(coderoot, flag)
    NOGITTAG
        returns ("NOTXTFILE", None)
                ("YESTXTFILE", "1.0.0")
    YESGITTAG
        returns ("NOTXTFILE", None)
                ("YESTXTFILE", "0.9.0")
  CASE 
  NOGITTAG and NOTXTFILE
     return datetime
  NOGITTAG and YESTXTFILE
     return txtfile_str
  YESGITTAG and NOTXTFILE
     set version file
     return gittag_str
  YESGITTAG and YESTXTFILE
     compare version file, set if needed
     return gittag_str

      
  
          
"""

import datetime
import os
from subprocess import check_output

class VersionError(Exception):
    pass


def get_versionfile(code_root):
    """We assume a file RELEASE_VERSION always exists next to 
       setup.py.  We always assume that the file holds one line, one string.

    return a (flag, string) if file is there and correct, else return (flag, None)
     """
    try:
        fo = open(os.path.join(code_root, "RELEASE_VERSION"), 'r')
    except IOError, e:
        return ("NOTXTFILE", None)

    #check validity of file ...
    line = fo.readline().strip()
    if line != '': 
        return ("YESTXTFILE", line)
    else:
        return ("NOTXTFILE", None)


def write_versionfile(code_root, versionstr):
    """We have discovered that RELEASE_VERSION either does not exist
       or has an (different/older) version number.
       Overwrite RELEASE_VERSION file

    """
    fo = open(os.path.join(code_root, "RELEASE_VERSION"), 'w')
    fo.write(versionstr.strip())
    fo.close()
    
def get_gitdescribe(code_root):
    """ 
    Given a dir, return the git describe value for it.
   
    Test assumes no one is git tracking tmp...

    >>> get_gitdescribe("/tmp")
    ('NOGITTAG', None)
    >>> get_gitdescribe("non/existent/dir")
    ('NOGITTAG', None)

    """
    try:
        ver = check_output(["git", "describe"], cwd=code_root).strip() 
        ### but git describe returns exit 0 if dir is not .git or no annotated tags
        if ver == '':
            git_release_str = None
            flag = "NOGITTAG"
        else:
            git_release_str = ver 
            flag = "YESGITTAG"
    except Exception, e:
        git_release_str = None
        flag = "NOGITTAG"
  
    return (flag, git_release_str)
    

def get_version(code_root):
    """
    retrieve from the code_root, which is *assumed* to be a git
    working dir the :cmd:`git describe` result

    
    can and should expand to handle a lot of edge cases

    :rating: **

    Normal case: in a git repo return tag based version

    >>> import os, subprocess, shutil
    >>> t = "/tmp/foo123"
    >>> os.mkdir(t)
    >>> junk = subprocess.check_output(["git", "init"], cwd=t)
    >>> junk = subprocess.check_output(["touch", "foo"], cwd=t)
    >>> junk = subprocess.check_output(["git", "add", "foo"], cwd=t)
    >>> junk = subprocess.check_output(["git", "commit", "-m", "'test'"], cwd=t)
    >>> junk = subprocess.check_output(["git", "tag", "-a", "0.0.1", "-m", "'test'"], cwd=t)
    >>> get_version(t) #normal case
    '0.0.1'
    >>> shutil.rmtree(t)

    
    No git directory, look for RELEASE_VERSION

    >>> t = "/tmp/foo123"
    >>> os.mkdir(t)
    >>> open(os.path.join(t, "RELEASE_VERSION"),'w').write("0.0.2-test")
    >>> get_version(t) #use txt file
    '0.0.2-test'
    >>> shutil.rmtree(t)

    Nothing in dir at all

    >>> t = "/tmp/foo123"
    >>> os.mkdir(t)
    >>> get_version(t) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    'versionfail...'
    >>> shutil.rmtree(t)

    """
    # START, GITTAG, TXTFILE, NEITHER
    ### Normal - grab git describe
    gitflag, gitstr = get_gitdescribe(code_root)
    txtflag, txtstr = get_versionfile(code_root)

    if (gitflag == "NOGITTAG" and txtflag == "NOTXTFILE"):
        # .. todo:: return UTC TZ
        release_str = 'versionfail-%s' % datetime.datetime.today().isoformat()
    elif (gitflag == "NOGITTAG" and txtflag == "YESTXTFILE"):
        release_str = txtstr
    elif (gitflag == "YESGITTAG" and txtflag == "NOTXTFILE"):
        release_str = gitstr
        write_versionfile(code_root, release_str)
    elif (gitflag == "YESGITTAG" and txtflag == "YESTXTFILE"):
        release_str = gitstr
        write_versionfile(code_root, release_str)
    else:
        # should never reach here.
        release_str = "SeriousVersionFail101"
    return release_str    






if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
