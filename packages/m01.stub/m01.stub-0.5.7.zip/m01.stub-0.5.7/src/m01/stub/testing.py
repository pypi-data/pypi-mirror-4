###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import os
import os.path
import zipfile
import sys
import shutil
import fnmatch
import datetime
import time
import tempfile
import urllib
import subprocess
import platform
import logging
import setuptools.archive_util

import pymongo.errors
import pymongo.connection

mongoPort = None
mongoHost = None

VERSION = '2.2.2'

LOGGER = logging.getLogger('m01.stub')

## XXX: implement linux, OSX detection and force using 64bit if True
#def is64bit():
#    """Returns True for 64 bit OS.
#    
#    Note: we will check for OS and not the chunk from the python 
#    platform or sys returns because everything which pyhton will return
#    depends on the installed python version and not on the OS version.
#
#    Also see:
#    http://blogs.msdn.com/b/david.wang/archive/2006/03/26/howto-detect-process-bitness.aspx
#    http://stackoverflow.com/questions/2764356/python-get-windows-os-version-and-architecture
#    http://bytes.com/topic/python/answers/509764-detecting-64bit-vs-32bit-linux
#
#    Test environment using this table:
#    
#      Environment Variable       32bit Native    64bit Native    WOW64
#      PROCESSOR_ARCHITECTURE     x86             AMD64           x86
#      PROCESSOR_ARCHITEW6432     undefined       undefined       AMD64
#
#    """
#    if sys.platform.startswith("linux"):
#        return platform.architecture()[0] == "64bit"
#    else:
#        PA = os.environ.get("PROCESSOR_ARCHITECTURE")
#        PAW6432 = os.environ.get("PROCESSOR_ARCHITEW6432")
#        return PA == "AMD64" or PAW6432 == "AMD64" 


# helper for zip and unzip mongodb for simpler sample data setup
def zipFolder(folderPath, zipPath, topLevel=False):
    """Zip a given folder to a zip file, topLevel stores top elvel folder too"""
    # remove existing zip file
    if os.path.exists(zipPath):
        os.remove(zipPath)
    zip = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
    path = os.path.normpath(folderPath)
    # os.walk visits every subdirectory, returning a 3-tuple of directory name,
    # subdirectories in it, and filenames in it
    for dirPath, dirNames, fileNames in os.walk(path):
        # walk over every filename
        for file in fileNames:
            # ignore hidden files
            if not file.endswith('.lock'):
                if topLevel:
                    fPath = os.path.join(dirPath, file)
                    relPath = os.path.join(dirPath, file)[len(path)+len(os.sep):]
                    arcName = os.path.join(os.path.basename(path), relPath)
                    zip.write(fPath, arcName)
                else:
                    fPath = os.path.join(dirPath, file)
                    relPath = os.path.join(dirPath[len(path):], file)
                    zip.write(fPath, relPath)
    zip.close()
    return None


def unZipFile(zipPath, target):
    # If the output location does not yet exist, create it
    if not os.path.isdir(target):
        os.makedirs(target)
    zip = zipfile.ZipFile(zipPath, 'r')
    for each in zip.namelist():
        # check to see if the item was written to the zip file with an
        # archive name that includes a parent directory. If it does, create
        # the parent folder in the output workspace and then write the file,
        # otherwise, just write the file to the workspace.
        if not each.endswith('/'):
            root, name = os.path.split(each)
            directory = os.path.normpath(os.path.join(target, root))
            if not os.path.isdir(directory):
                os.makedirs(directory)
            file(os.path.join(directory, name), 'wb').write(zip.read(each))
    zip.close()


# support missing ignore pattern in py25
def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter"""
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns


def copytree(src, dst, ignore=None):
    """Recursively copy a directory tree using copy2()"""
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, ignore)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors



def doRemoveTree(src, sleep=5, retry=0):
    while retry <= 3:
        retry += 1
        try:
            if os.path.exists(src):
                LOGGER.info("remove directory %s" % src)
                shutil.rmtree(src)
        except Exception, e: # WindowsError, OSError?, just catch anything
            # this was to early just try again
            LOGGER.error("can't remove directory %s" % src)
            time.sleep(sleep)
            doRemoveTree(src, sleep, retry)
        # break while if everything is fine
        break

def waitForMongoStartup(host, port, sleep):
    """Wait for the mongo to answer a status command.
    
    We are not currently checking for any specific value, just an "OK" answer.
    """
    connection = pymongo.connection.Connection(host, port)
    for x in range(int(sleep)):
        status = connection.admin.command('serverStatus').get('ok')
        if status == '1.0':
            LOGGER.info("mognodb started")
            break
        time.sleep(1)


def startMongoDBServer(host='localhost', port=45017, options=None,
    sandBoxDir=None, dataDir=None, logDir=None, dataSource=None, sleep=5.0,
    dataSourceCopyTreeIgnorePatterns='*.svn', downloadURL=None,
    force64bit=True, version=None, logLevel=10):
    """Start the mongodb test server.

    NOTE: there is one important thing. You allways need to make sure that you
    use a new connection in each test using this setup. Otherwise a new test
    will reuse a connection from a previous connection pool setup. (pymongo)
    """
    if version is None:
        version = VERSION

    # setup server folder
    if sandBoxDir is None:
        here = os.path.dirname(__file__)
        sandbox = os.path.join(here, 'sandbox')
    else:
        sandbox = sandBoxDir

    # setup data dir
    if dataDir is None:
        data = os.path.join(sandbox, 'data')
    else:
        data = dataDir

    # setup logs dir
    if logDir is None:
        logs = os.path.join(sandbox, 'logs')
    else:
        logs = logDir

    # setup sandbox folder
    if not os.path.exists(sandbox):
        os.mkdir(sandbox)

    # download and install a server
    if not 'bin' in os.listdir(sandbox):
        arch = platform.architecture()[0]
        # explicit download url
        if downloadURL:
            url = downloadURL
        # windows
        elif os.name == 'nt' and (force64bit or arch == '64bit'):
            url = 'http://downloads.mongodb.org/win32/mongodb-win32-x86_64-%s.zip' % version
        elif os.name == 'nt' and arch == '32bit':
            url = 'http://downloads.mongodb.org/win32/mongodb-win32-i386-%s.zip' % version
        # mac
        elif sys.platform == 'darwin' (force64bit or arch == '64bit'):
            url = 'http://fastdl.mongodb.org/osx/mongodb-osx-x86_64-%s.tgz' % version
        elif sys.platform == 'darwin' and arch == '32bit':
            url = 'http://fastdl.mongodb.org/osx/mongodb-osx-i386-%s.tgz' % version
        # posix
        elif os.name == 'posix' and (force64bit or arch == '64bit'):
            url = 'http://fastdl.mongodb.org/linux/mongodb-linux-x86_64-%s.tgz' % version
        elif os.name == 'posix' and arch == '32bit':
            url = 'http://fastdl.mongodb.org/linux/mongodb-linux-i686-%s.tgz' % version
        else:
            raise ValueError("No download found, define a downloadURL")

        LOGGER.info("download mongodb installer")
        tmpDir = tempfile.mkdtemp('m01-stub-download-tmp')
        handle, downloadFile = tempfile.mkstemp(prefix='m01-stub-download')
        urllib.urlretrieve(url, downloadFile)
        setuptools.archive_util.unpack_archive(downloadFile, tmpDir)
        topLevelDir = os.path.join(tmpDir, os.listdir(tmpDir)[0])
        for fName in os.listdir(topLevelDir):
            source = os.path.join(topLevelDir, fName)
            dest = os.path.join(sandbox, fName)
            shutil.move(source, dest)

        # cleanup
        doRemoveTree(tmpDir, sleep)
        try:
            os.remove(downloadFile)
        except OSError:
            pass

    # first remove the original data folder, we need an empty setup
    if os.path.exists(data):
        doRemoveTree(data, sleep)

    # re-use predefined mongodb data for simpler testing
    if dataSource is not None and os.path.exists(dataSource):
        if dataSource.endswith('.zip'):
            # extract zip file to dataDir
            try:
                LOGGER.info("unzip data source")
                unZipFile(dataSource, data)
            except Exception, e: # WindowsError?, just catch anything
                doRemoveTree(data, sleep)
                unZipFile(dataSource, data)
        else:
            # copy source folder to dataDir
            ignore = None
            if dataSourceCopyTreeIgnorePatterns is not None:
                ignore = ignore_patterns(dataSourceCopyTreeIgnorePatterns)
            try:
                LOGGER.info("copy data source")
                copytree(dataSource, data, ignore=ignore)
            except Exception, e: # WindowsError?, just catch anything
                # this was to early just try again
                doRemoveTree(data, sleep)
                copytree(dataSource, data, ignore=ignore)

    # ensure new data location if not created with dataSource
    if not os.path.exists(data):
        try:
            LOGGER.info("make data dir % " % data)
            os.mkdir(data)
        except Exception, e:
            # this was to early just try again
            time.sleep(sleep)
            os.mkdir(data)

    # start the mongodb stub server
    if os.name == 'nt':
        mongod = os.path.join(sandbox, 'bin', 'mongod.exe')
    else:
        mongod = os.path.join(sandbox, 'bin', 'mongod')
    cmd = [mongod]

    if os.name == 'nt':
        data = '"%s"' % data
    if options is None:
        # default options if non explicit given
        cmd.extend([# smaller file size for faster start/stop
                    '--nojournal', '--smallfiles', '--nssize', '100',
                    # add dbpath
                    '--dbpath', data])
    else:
        cmd.extend(options)
        cmd.append(data)

    # setup log dir
    if '--logpath' not in cmd:
        if not os.path.exists(logs):
            os.mkdir(logs)
        now = datetime.datetime.utcnow()
        ts = '%s.%3d' % (now.strftime("%Y%m%d-%H-%M-%S"),
            now.microsecond / 1000)
        logPath = '"%s"' % os.path.join(logs, 'm01.stub.%s.log' % ts)
        cmd.extend(['-v', '--logpath', logPath])
        # only logs to working directory
        #cmd.extend(['--logpath', 'm01-stub.log'])

    # set host
    if host != 'localhost':
        cmd.append(host)
    global mongoHost
    mongoHost = host

    # set port
    if port != 27017:
        cmd.extend(['--port', str(port)])
    global mongoPort
    mongoPort = port

    if os.name == 'nt':
        stdout = stderr = None
    else:
        cmd.append('--fork')
        stdout = stderr = subprocess.PIPE

    # append run cmd
    cmd.append('run')

    if os.name == 'nt':
        cmd = ' '.join(cmd)

    # start mongodb server
    try:
        LOGGER.info("start mongodb server with: %s" % cmd)
        p = subprocess.Popen(cmd, shell=False, stdout=stdout, stderr=stderr)
    except Exception, e:
        raise Exception("Subprocess error: %s" % e)

    waitForMongoStartup(host, port, 16)

def stopMongoDBServer(sleep=2.0):
    global mongoHost
    global mongoPort
    connection = pymongo.connection.Connection(mongoHost, mongoPort)
    LOGGER.info("stop mongodb server at %s:%s" % (mongoHost, mongoPort))
    for x in range(5):
        try:
            status = connection.admin.command('shutdown')
            LOGGER.info("mognodb stopped % " % status)
        except pymongo.errors.ConnectionFailure:
            # successfully shut down
            break
        time.sleep(1)
    # wait some seconds to stop the mongodb server
    time.sleep(sleep)
    mongoHost = None
    mongoPort = None


###############################################################################
#
# Doctest setup
#
###############################################################################

def doctestSetUp(test):
    # setup mongodb server
    startMongoDBServer()


def doctestTearDown(test):
    # tear down mogodb server
    stopMongoDBServer()
