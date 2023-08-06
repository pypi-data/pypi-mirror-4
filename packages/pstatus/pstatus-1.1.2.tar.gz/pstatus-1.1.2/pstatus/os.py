'''
pstatus.os
----------

``pstatus.os`` exports ``system``, ``wait``, ``wait3``, ``wait4``, and
``waitpid`` which shadow the functions with the same name in the standard
library's ``os`` module, but instead of returning a raw status code, returns a
split tuple which includes an exit code, a signal number, a flag indicating
whether or not te process has left a core dump.
'''
from __future__ import absolute_import

import os
from .main import split
from .models import PRStatus
from .models import PStatus
from .models import Status

__all__ = ['system', 'wait', 'wait3', 'wait4', 'waitpid']


def system(command):
    """
    Execute the command (a string) in a subshell

    Split the exit status code into a ``tuple`` which includes the processes
    exit code, the signal responsible for the processes termination, and
    whether or not the process left a core dump behind. If there was no exit
    code then the first value will be ``None``, and if there was no signal,
    then the second value will be ``None``.

    >>> system('true')
    Status(exit=0, signal=None, core=False)

    :param command: command to run
    :type command: ``string``
    :returns:  ``3-tuple`` (exit, signal, core)
    :rtype: ``3-tuple``
    """
    status = os.system(command)
    return split(status)


def wait():
    """
    Wait for completion of a child process.

    Returns the pid of the completed child process and it's exit status code
    split into a ``tuple`` which includes the processes exit code, the signal
    responsible for the processes termination, and whether or not the process
    left a core dump behind. If there was no exit code then the first value
    will be ``None``, and if there was no signal, then the second value will be
    ``None``.

    >>> pid = os.spawnlp(os.P_NOWAIT, 'true', 'true')
    >>> wait()  # doctest: +ELLIPSIS
    Status(pid=..., exit=0, signal=None, core=False)

    :returns:  ``4-tuple`` (pid, exit, signal, core)
    :rtype: ``4-tuple``
    """
    pid, status = os.wait()
    return PStatus(pid, *split(status))


def wait3(options):
    """
    Wait for completion of a child process.

    Returns the pid of the completed child process, it's rusage,  and it's exit
    status code split into a ``tuple`` which includes the processes exit code,
    the signal responsible for the processes termination, and whether or not
    the process left a core dump behind. If there was no exit code then the
    first value will be ``None``, and if there was no signal, then the second
    value will be ``None``.

    >>> pid = os.spawnlp(os.P_NOWAIT, 'true', 'true')
    >>> wait3(0)  # doctest: +ELLIPSIS
    Status(pid=..., exit=0, signal=None, core=False, rusage=...)

    :param options: options for wait
    :type options: ``int``
    :returns:  ``5-tuple`` (pid, exit, signal, core, rusage)
    :rtype: ``5-tuple``
    """
    pid, status, rusage = os.wait3(options)
    exit_, signal, core = split(status)
    return PRStatus(pid, exit_, signal, core, rusage)


def wait4(pid, options):
    """
    Wait for completion of a given child process.

    Returns the pid of the completed child process, it's rusage,  and it's exit
    status code split into a ``tuple`` which includes the processes exit code,
    the signal responsible for the processes termination, and whether or not
    the process left a core dump behind. If there was no exit code then the
    first value will be ``None``, and if there was no signal, then the second
    value will be ``None``.

    If ``pid`` is greater than `0`, ``waitpid()`` requests status information
    for that specific process. If ``pid`` is ``0``, the request is for the
    status of any child in the process group of the current process. If ``pid``
    is ``-1``, the request pertains to any child of the current process. If
    ``pid`` is less than ``-1``, status is requested for any process in the
    process group ``-pid`` (the absolute value of ``pid``).

    >>> pid = os.spawnlp(os.P_NOWAIT, 'true', 'true')
    >>> wait4(pid, 0)  # doctest: +ELLIPSIS
    Status(pid=..., exit=0, signal=None, core=False, rusage=...)

    :param pid: pid to wait for
    :type pid: ``int``
    :param options: options for wait
    :type options: ``int``
    :returns:  ``5-tuple`` (pid, exit, signal, core, rusage)
    :rtype: ``5-tuple``
    """
    pid, status, rusage = os.wait4(pid, options)
    exit_, signal, core = split(status)
    return PRStatus(pid, exit_, signal, core, rusage)


def waitpid(pid, options):
    """
    Wait for completion of a given child process.

    Returns the pid of the completed child process and it's exit status code
    split into a ``tuple`` which includes the processes exit code, the signal
    responsible for the processes termination, and whether or not the process
    left a core dump behind. If there was no exit code then the first value
    will be ``None``, and if there was no signal, then the second value will be
    ``None``.

    If ``pid`` is greater than `0`, ``waitpid()`` requests status information
    for that specific process. If ``pid`` is ``0``, the request is for the
    status of any child in the process group of the current process. If ``pid``
    is ``-1``, the request pertains to any child of the current process. If
    ``pid`` is less than ``-1``, status is requested for any process in the
    process group ``-pid`` (the absolute value of ``pid``).

    >>> pid = os.spawnlp(os.P_NOWAIT, 'true', 'true')
    >>> waitpid(pid, 0)  # doctest: +ELLIPSIS
    Status(pid=..., exit=0, signal=None, core=False)

    :param pid: pid to wait for
    :type pid: ``int``
    :param options: options for wait
    :type options: ``int``
    :returns:  ``4-tuple`` (pid, exit, signal, core)
    :rtype: ``4-tuple``
    """
    pid, status = os.waitpid(pid, options)
    return PStatus(pid, *split(status))
