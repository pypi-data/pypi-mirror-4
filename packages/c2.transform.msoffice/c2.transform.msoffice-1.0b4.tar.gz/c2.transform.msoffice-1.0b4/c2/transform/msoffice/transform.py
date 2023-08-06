#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import signal
import mimetypes
import subprocess
if sys.platform == 'win32':
    isWIN = True
    import time
    try:
        import ctypes
    except ImportError:
        ctypes = None
else:
    isWIN = False
    import select
    import time
    import threading

from zope.interface import implements
try:
    from Products.PortalTransforms.interfaces import ITransform
    HAS_PLONE3 = False
except ImportError:
    from Products.PortalTransforms.interfaces import itransform
    HAS_PLONE3 = True
from config import SITE_CHARSET, TRANSFORM_NAME
from c2.transform.msoffice import logger

scpath = os.path.join(os.path.dirname(__file__), 'msdoc2txt.jar')

def win_kill(pid):
    if ctypes:
        h = ctypes.windll.kernel32.OpenProcess(1, False, pid)
        ctypes.windll.kernel32.TerminateProcess(h, -1)
        ctypes.windll.kernel32.CloseHandle(h)
    else:
        subprocess.call(["TASKKILL", "/PID", str(pid), "/F"])

def win_timeout(p, timeout):
    s = time.time()
    while time.time() - s < timeout and p.poll() == None:
        time.sleep(0.1)
    if p.poll() == None:
        win_kill(p.pid)
        return False
    return True

def msdoc2txt(data, timeout=60): #default 60 sec
    assert isinstance(data, str)
    p = subprocess.Popen(("java", '-jar', '-Xmx512m', scpath),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    if not isWIN:
        # Based on the code from http://betabug.ch/blogs/ch-athens/1093
        kill_check = threading.Event()
        def _kill_process_after_a_timeout(pid):
            os.kill(pid, signal.SIGTERM)
            kill_check.set() # tell the main routine that we had to kill
            # use SIGKILL if hard to kill...
            return

        pid = p.pid
        watchdog = threading.Timer(timeout, _kill_process_after_a_timeout, args=(pid, ))
        watchdog.start()
        (out,err) = p.communicate(input=data)
        watchdog.cancel() # if it's still waiting to run
        success = not kill_check.isSet()
        kill_check.clear()

        if success:
            if err:
                status = False
                val = err
            elif out:
                status = True
                val = out
        else:
            status = None
            val = "timeout" #if timeout

        return status, val
    else:
        r = win_timeout(p, timeout)
        if r:
            if p.poll():
                return False, p.stderr.read() #if fail
            else:
                return True, p.stdout.read() #if not fail
        else:
            return None, "timeout" #if timeout


class msoffice_to_text:
    if HAS_PLONE3:
        __implements__ = itransform
    else:
        implements(ITransform)
    __name__ = TRANSFORM_NAME

    inputs = (
        # MS-Word formats
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-word.document.macroEnabled.12',
        # MS-Excle formats
        'application/vnd.ms-excel',
        'application/msexcel',
        'application/x-msexcel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
        'application/vnd.ms-excel.sheet.macroEnabled.12',
        # MS-PowerPoint formats
        'application/powerpoint',
        'application/mspowerpoint',
        'application/x-mspowerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
        )

    output = 'text/plain'

    output_encoding = SITE_CHARSET

    def __init__(self,name=None):
        if name:
            self.__name__=name
        return

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        #orig_file = kwargs.get('filename') or 'unknown.xxx'
        mimetype = kwargs.get('mimetype')
        filename = kwargs.get('filename') or 'unknown.xxx'

        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0]
        try:
            status, text = msdoc2txt(orig)
        except Exception, e:
            logger.error(e, exc_info=True)
            data.setData('')
            return data
        if status:
            data.setData(text)
        else:
            logger.error(text, exc_info=True)
            data.setData('')
        return data

def register():
    return msoffice_to_text()
