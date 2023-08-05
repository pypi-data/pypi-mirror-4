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


"""

import datetime
import os
from subprocess import check_output

class VersionError(Exception):
    pass

def get_version(code_root):
    return get_gitdescribe(code_root)


def get_versionfile(code_root):
    """We assume a file RELEASE_VERSION always exists next to 
       setup.py.  We always assume that the file holds one line, one string.

    return a string if file is there and correct, else return None
     """
    try:
        fo = open(os.path.join(code_root, "RELEASE_VERSION"), 'r')
    except IOError, e:
        return None

    #check validity of file ...
    line = fo.readline().strip()
    if line != '': 
        return line
    else:
        return None
    fo.close()

def write_versionfile(code_root, versionstr):
    """We have discovered that RELEASE_VERSION either does not exist
       or has an (different/older) version number.
       Overwrite RELEASE_VERSION file

    """
    fo = open(os.path.join(code_root, "RELEASE_VERSION"), 'w')
    fo.write(versionstr)
    fo.close()
    

def get_gitdescribe(code_root):
    """
    retrieve from the code_root, which is *assumed* to be a git
    working dir the :cmd:`git describe` result

    
    can and should expand to handle a lot of edge cases

    :rating: **

    """

    git_release_str = ''
    txt_release_str = ''

    ### Normal - grab git describe
    try:
        ver = check_output(["git", "describe"], cwd=code_root).strip() 
#        branch = check_output(["git", "branch"], cwd=code_root).strip()
#        for line in branch.split('\n'):
#            if line.find("*") == 0:
#                currbranch = line.replace("*","").strip()

        ## failed if ver is '', local exceptions hidden by fabric !!
        if (ver == None or ver == ''):
            raise VersionError("Failed to get git from %s" % code_root)

        #exception if no currbranch
        git_release_str = ver 
        

    ## ok - git describe did not work - now is there a RELEASE_VERSION file?
    except Exception, e:
        try:
            txt_release_str = get_versionfile(code_root)
        except IOError, e:
            txt_release_str = ''

    ###..todo::  this is messy ... rethink it
    finally:
        if (git_release_str == '' and txt_release_str == ''):
            release_str = 'version-fail-%s' % datetime.datetime.today().isoformat()             
        if git_release_str != '':
            release_str = git_release_str
        if (txt_release_str != '' and git_release_str == ''):
            release_str = txt_release_str
        if (git_release_str != txt_release_str and git_release_str != ''):
            write_versionfile(code_root, git_release_str)
         
    return release_str





