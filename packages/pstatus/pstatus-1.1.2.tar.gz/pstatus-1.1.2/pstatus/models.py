from __future__ import absolute_import

from collections import namedtuple


class Status(namedtuple('Status', ['exit', 'signal', 'core'])):
    """
    This object may be accessed as either a ``tuple`` of ``(exit, signal,
    core)`` or via the attributes ``exit``, ``signal``, and ``core``.
    Additionally another attribute ``ok`` is defined which indicates whether or
    not the process exited successfully.
    """
    @property
    def ok(self):
        """
        Returns whether or not the process exited successfully
        """
        return (self.exit == 0)

class PStatus(namedtuple('Status', ['pid', 'exit', 'signal', 'core'])):
    """
    This object may be accessed as either a ``tuple`` of ``(pid, exit, signal,
    core)`` or via the attributes ``pid``, ``exit``, ``signal``, and ``core``.
    Additionally another attribute ``ok`` is defined which indicates whether or
    not the process exited successfully.
    """
    @property
    def ok(self):
        """
        Returns whether or not the process exited successfully
        """
        return (self.exit == 0)

class PRStatus(namedtuple('Status', ['pid', 'exit', 'signal', 'core', 'rusage'])):
    """
    This object may be accessed as either a ``tuple`` of ``(pid, exit, signal,
    core, rusage)`` or via the attributes ``pid``, ``exit``, ``signal``,
    ``core``, and ``rusage``.  Additionally another attribute ``ok`` is defined
    which indicates whether or not the process exited successfully.
    """
    @property
    def ok(self):
        """
        Returns whether or not the process exited successfully
        """
        return (self.exit == 0)
