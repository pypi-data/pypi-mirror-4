# Example: daemonize pyinotify's notifier.
#
# Requires Python >= 2.5
import functools
import sys
import pyinotify

class Counter(object):
    """
    Simple counter.
    """
    def __init__(self):
        self.count = 0
    def plusone(self):
        self.count += 1

def on_loop(notifier, counter):
    """
    Dummy function called after each event loop, this method only
    ensures the child process eventually exits (after 5 iterations).
    """
    if counter.count > 4:
        # Loops 5 times then exits.
        sys.stdout.write("Exit\n")
        notifier.stop()
        sys.exit(0)
    else:
        sys.stdout.write("Loop %d\n" % counter.count)
        counter.plusone()

wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm)
wm.add_watch('/tmp', pyinotify.ALL_EVENTS)
on_loop_func = functools.partial(on_loop, counter=Counter())

# Notifier instance spawns a new process when daemonize is set to True. This
# child process' PID is written to /tmp/pyinotify.pid (it also automatically
# deletes it when it exits normally). If no custom pid_file is provided it
# would write it more traditionally under /var/run/. /tmp/stdout.txt is used
# as stdout stream thus traces of events will be written in it, force_kill
# means that if there is already an /tmp/pyinotify.pid with a corresponding
# running process it will be killed first. callback is the above function
# and will be called after each event loop.
notifier.loop(daemonize=True, callback=on_loop_func,
              pid_file='/tmp/pyinotify.pid', force_kill=True,
              stdout='/tmp/stdout.txt')
