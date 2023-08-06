'''
pstatus
-------

``pstatus`` is can be used to extract meaning from process status codes as
returned by ``os.system``, ``os.wait``, ``os.waitpid``, as well as
``subprocess.call``, ``subprocess.CalledProcessError.returncode``,
``subprocess.Popen.call``, ``subprocess.Popen.wait``, and
``subprocess.Popen.returncode``.

It exports a function ``split`` which extracts an exit code, a signal number, a
flag indicating whether or not the process left a core dump behind.

'''
from __future__ import absolute_import

from .models import Status
from .main import split
from . import os

__version__ = '1.1.2'

__all__ = ['split']
