"""
The following script has been created in order to give quick timing statistics
"""
from datetime import datetime
class timing(object):
    __author__ = 'Kenan Bolat'
    __copyright__ = "2018, Kenan Bolat"
    def __init__(self):
        self.startTime = datetime.now()
        self.lastCallTime = self.startTime
    def _calculate_time_difference(self, now, then):
        self.lastCallTime = now
        return now - then
    ## TODO incremental and step by step time differences
    def incremental_runtime(self):
        return self._calculate_time_difference(datetime.now(), self.lastCallTime)
    def runtime(self):
        return self._calculate_time_difference(datetime.now(), self.startTime)
