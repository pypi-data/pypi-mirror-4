Status-code helper utilities
============================

pstatus is can be used to extract meaning from process status codes as returned
by ``os.system``, ``os.wait``, ``os.waitpid``, as well as ``subprocess.call``,
``subprocess.CalledProcessError.returncode``, ``subprocess.Popen.call``,
``subprocess.Popen.wait``, and ``subprocess.Popen.returncode``.

It exports a function ``split`` which extracts an exit code, a signal number, a
flag indicating whether or not the process left a core dump behind.

Also includes a module ``pstatus.os`` which exports ``system``, ``wait``,
``wait3``, ``wait4``, and ``waitpid``. Each of these shadow the functions with
the same name in the standard library's ``os`` module, but instead of returning
a status code, returns a split tuple.

``API`` documentation is available at ReadTheDocs_.


pstatus
-------

pstatus.split
~~~~~~~~~~~~~

With ``os.system``:

>>> split(os.system('true'))
Status(exit=0, signal=None, core=False)
>>> split(os.system('false'))
Status(exit=1, signal=None, core=False)

Using ``os.spawnlp`` and ``os.kill`` to demonstrate extraction of signals:

>>> pid = os.spawnlp(os.P_NOWAIT, 'sleep', 'sleep', '100')
>>> os.kill(pid, 15)
>>> _, code = os.waitpid(pid, 0)
>>> split(code)
Status(exit=None, signal=15, core=False)

With ``subprocess.call``:

>>> import subprocess
>>> split(subprocess.call(['true']), subprocess=True)
Status(exit=0, signal=None, core=None)
>>> split(subprocess.call(['false']), subprocess=True)
Status(exit=1, signal=None, core=None)

Using ``subprocess.Popen`` and ``subprocess.Popen.kill`` to extract
signals:

>>> p = subprocess.Popen(['sleep', '100'])
>>> p.terminate()
>>> split(p.wait(), subprocess=True)
Status(exit=None, signal=15, core=None)


pstatus.os
----------

pstatus.os.system
~~~~~~~~~~~~~~~~~

Shadows ``os.system`` and returns split status information.

>>> system('true')
Status(exit=0, signal=None, core=False)

pstatus.os.wait
~~~~~~~~~~~~~~~

Shadows ``os.wait`` and returns split status information with a pid.

>>> pid = os.spawnlp(os.P_NOWAIT, 'true', 'true')
>>> wait()
Status(pid=12345, exit=0, signal=None, core=False)

pstatus.os.wait3
~~~~~~~~~~~~~~~~

Shadows ``os.wait3`` and returns split status information with a pid and rusage.

>>> pid = os.spawnlp(os.P_NOWAIT, 'true', 'true')
>>> wait3(0)
Status(pid=12345, exit=0, signal=None, core=False, rusage=resource.struct_rusage(ru_utime=0.0017259999999999999, ru_stime=0.0018889999999999998, ru_maxrss=499712, ru_ixrss=0, ru_idrss=0, ru_isrss=0, ru_minflt=495, ru_majflt=0, ru_nswap=0, ru_inblock=0, ru_oublock=0, ru_msgsnd=0, ru_msgrcv=0, ru_nsignals=0, ru_nvcsw=0, ru_nivcsw=2))

pstatus.os.wait4
~~~~~~~~~~~~~~~~

Shadows ``os.wait4`` and returns split status information with a pid and rusage.

>>> pid = os.spawnlp(os.P_NOWAIT, 'true', 'true')
>>> wait4(pid, 0)
Status(pid=12345, exit=0, signal=None, core=False, rusage=resource.struct_rusage(ru_utime=0.0017259999999999999, ru_stime=0.0018889999999999998, ru_maxrss=499712, ru_ixrss=0, ru_idrss=0, ru_isrss=0, ru_minflt=495, ru_majflt=0, ru_nswap=0, ru_inblock=0, ru_oublock=0, ru_msgsnd=0, ru_msgrcv=0, ru_nsignals=0, ru_nvcsw=0, ru_nivcsw=2))

pstatus.os.waitpid
~~~~~~~~~~~~~~~~~~

Shadows ``os.waitpid`` and returns split status information with a pid.

>>> pid = os.spawnlp(os.P_NOWAIT, 'true', 'true')
>>> waitpid(pid, 0)
Status(pid=12345, exit=0, signal=None, core=False)


.. _ReadTheDocs: https://pstatus.readthedocs.org/en/latest/
