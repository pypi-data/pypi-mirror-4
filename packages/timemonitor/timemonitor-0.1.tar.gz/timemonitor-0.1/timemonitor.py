import timeit
from collections import defaultdict

_monitors = None
_format = "%-10s : %.3f s\n"

def reset():
    global _monitors
    _monitors = defaultdict(lambda : 0) 

def summarize(format=_format):
    out = "Time Monitor\n"
    for k in sorted(_monitors.keys()):
        out += format % (k, _monitors[k])
    return out

class TimeMonitor:

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = timeit.default_timer()
        return self

    def __exit__(self, *args):
        self.end = timeit.default_timer()
        self.interval = self.end - self.start
        global _monitors
        _monitors[self.name] += self.interval

# set initial values for _monitors
reset()
