from __future__ import absolute_imports

class NagiosReturnCode(object):
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    

class NagiosCheckResult(object):
    def __init__(self, success=True, summary=None, perfdata=None, details=None):
        self.success = success
        pass
