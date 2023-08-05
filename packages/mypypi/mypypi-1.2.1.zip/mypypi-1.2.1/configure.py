##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import getpass
import os
import sys
import string
import shutil
import time

from codecs import getencoder
try:
    from hashlib import md5, sha1
except ImportError:
    # Python 2.4
    from md5 import new as md5
    from sha import new as sha1

try:
    # during bootstrap, we don't know the buildout location, but that's fine
    import zc.buildout.buildout
    isBootstrap = False
except ImportError:
    isBootstrap = True


def backupFile(fileName):
    t = time.time()
    lt = time.localtime(t)
    tStr = time.strftime('%Y%m%d-%H-%M', lt)
    backupFileName = fileName +'-'+ tStr
    shutil.copyfile(fileName, backupFileName)

def makeTemplateFile(outName, data):
    if os.path.exists(outName):
        backupFile(outName)
    templ = string.Template(open(outName + '.in').read())
    outfile = open(outName, 'w')
    outfile.write(templ.substitute(data))
    outfile.close()
    print "Generated configuration file '%s'" % outName


def configureBuildout(sourcePath):
    # collect server settings
    dm = raw_input('Would you like to setup with devmode (y/n): ')
    if dm == 'y':
        devMode = True
    elif dm == 'n':
        devMode = False
    else:
        raise ValueError("Bad devmode given. Only value 'y' or 'n' is allowed.")

    hostName = raw_input('Choose your server hostname: ')
    if not hostName:
        raise ValueError("No hostname given")

    hostPort = raw_input('Choose your server port: ')
    try:
        int(hostPort)
    except:
        raise ValueError("Port is not a number")

    if hostPort != 80:
        print "Note:"
        print "Distutils does not work with a port other then 80."
        print "Use a proxy server running at port 80 for access the "
        print "MyPyPi server at port %s" % hostPort
        print

    login = raw_input('Choose a managment user login: ')
    password = ''
    confirm = None
    while password != confirm:
        password = getpass.getpass('Choose a management user password: ')
        confirm = getpass.getpass('Confirm password: ')
        if password != confirm:
            password = ''
            confirm = None
            print "Password and confirm don't match!"
    pm = raw_input('Choose a password encryption (plain/md5/sha1): ')
    _encoder = getencoder("utf-8")
    if pm == 'plain':
        passwordManager = 'Plain Text'
    elif pm == 'md5':
        passwordManager = 'MD5'
        password = md5(_encoder(password)[0]).hexdigest()
    elif pm == 'sha1':
        passwordManager = 'SHA1'
        password = sha1(_encoder(password)[0]).hexdigest()
    else:
        raise ValueError("No password encryption choosen")

    # prepare template data
    data = {'VAR_ZCONFIG' :'${var:zconfig}',
            'VAR_PATH' :'${var:path}',
            'BUILDOUT_DIRECTORY': '${buildout:directory}',
            'HOST_NAME': hostName,
            'HOST_PORT': hostPort,
            'LOGIN': login,
            'PASSWORD': password,
            'PASSWORD_MANAGER': passwordManager}

    if devMode:
        data['DEVMODE'] = '<meta:provides feature="devmode" />'
    else:
        data['DEVMODE'] = '<!-- devmode disabled -->'

    # build app.cfg
    appCFG = os.path.join(sourcePath, 'app.cfg')
    makeTemplateFile(appCFG, data)

    print
    print "---------------------------------------------------------------"
    print "    New buildout configuration files successfully created"
    print ""
    print "           !!! You have to run buildout now !!!"
    if hostPort != 80:
        print ""
        print "    Note:"
        print "    Distutils does not work with a port other then 80."
        print "    Use a proxy server running at port 80 for access the "
        print "    MyPyPi server at port %s" % hostPort
    print ""
    print "---------------------------------------------------------------"


def main(sourcePath):
    configureBuildout(sourcePath)

if __name__ == '__main__':
    main(os.path.dirname(__file__))