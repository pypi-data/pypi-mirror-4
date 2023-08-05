#!/usr/bin/env python
"""Campari: command-line pomodoro timer.

Usage:
    campari run [--pomodoro=<pt>] [--shortbreak=<bt>] [--longbreak=<lt>]
    campari status
    campari next
    campari reset
    campari quit
    campari -h | --help
"""
import sys
import subprocess
from time import sleep
from decorator import decorator
from threading import RLock, Thread, Event
from datetime import datetime, timedelta
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from docopt import docopt
from version import VERSION

PORT = 31337
LONGBREAK_POMODOROS = 4


class RPCServer(SimpleXMLRPCServer):
    def __init__(self, *args, **kwargs):
        super(RPCServer, self).__init__(*args, **kwargs)
        self.stop_flag = False

    def serve_forever(self):
        while not self.stop_flag:
            self.handle_request()

    def stop(self):
        self.stop_flag = True


class Timer(Thread):
    def __init__(self, delay, func):
        super(Timer, self).__init__()
        self.delay = delay
        self.func = func
        self.cancel_event = Event()

    def run(self):
        while not self.cancel_event.is_set():
            sleep(self.delay)
            self.func()

    def cancel(self):
        self.cancel_event.set()


@decorator
def synchronized(method, self, *args, **kwargs):
    with self.rlock:
        return method(self, *args, **kwargs)


def notify(text):
    #subprocess.call(("notify-send", text))
    subprocess.call(("twmnc", text))


def timedelta_str(td):
    (total_minutes, seconds) = divmod(td.seconds, 60)
    (hours, minutes) = divmod(total_minutes, 60)
    result = "{0:02d}:{1:02d}".format(minutes, seconds)
    if hours > 0:
        result = "{0:2d}:{1}".format(hours, result)
    return result


class Counter(object):
    IDLE = "Idle"
    POMODORO = "Pomodoro"
    SHORTBREAK = "Short break"
    LONGBREAK = "Long break"

    def __init__(self, pomodoro=None, shortbreak=None, longbreak=None):
        self.rlock = RLock()
        self.times = {
            Counter.POMODORO: int(pomodoro or 25),
            Counter.SHORTBREAK: int(shortbreak or 5),
            Counter.LONGBREAK: int(longbreak or 15)}
        self.reset()

    @synchronized
    def reset(self):
        self.pomodoros_completed = 0
        self.finished = False
        self.set_state(Counter.IDLE)

    @synchronized
    def next_state(self, start_time=None):
        if self.state == Counter.POMODORO:
            self.pomodoros_completed += 1
            if self.pomodoros_completed % LONGBREAK_POMODOROS == 0:
                self.set_state(Counter.LONGBREAK)
            else:
                self.set_state(Counter.SHORTBREAK)
        else:
            assert(self.state in [Counter.IDLE,
                                  Counter.SHORTBREAK,
                                  Counter.LONGBREAK])
            self.set_state(Counter.POMODORO, start_time=start_time)

    @synchronized
    def set_state(self, new_state, start_time=None):
        self.state = new_state
        planned_minutes = self.times.get(self.state, 0)
        self.planned_time = timedelta(minutes=planned_minutes)
        self._start_time = start_time or datetime.now()
        self.update(self._start_time)
        self.finished = False

    @synchronized
    def status(self):
        result = self.state
        if self.state != Counter.IDLE:
            if self.finished:
                result += " DONE!"
            else:
                result += " " + timedelta_str(self._elapsed_time)
        return result

    @synchronized
    def update(self, now=None):
        if self.finished:
            return
        if now is None:
            now = datetime.now()
        spent_time = now - self._start_time
        zero = timedelta(seconds=0)
        self._elapsed_time = max(zero, self.planned_time - spent_time)
        if (self.state != Counter.IDLE and not self.finished
                and self._elapsed_time <= zero):
            self.finished = True
            notify(self.status())
            #self.next_state()


def run_server(counter):
    server = RPCServer(("localhost", PORT), allow_none=True)
    server.register_introspection_functions()
    server.register_instance(counter)
    server.register_function(server.stop, "quit")
    server.serve_forever()


def main():
    args = docopt(__doc__, version="Campari " + VERSION)
    if args["run"]:
        counter = Counter(
            pomodoro=args["--pomodoro"],
            shortbreak=args["--shortbreak"],
            longbreak=args["--longbreak"])
        # TODO: move delay to config
        timer = Timer(0.5, counter.update)
        timer.start()
        run_server(counter)
        timer.cancel()
        return
    proxy = ServerProxy("http://localhost:{0}".format(PORT))
    if args["status"]:
        try:
            print(proxy.status())
        except:
            print("ERROR")
    elif args["next"]:
        proxy.next_state()
        print(proxy.status())
    elif args["reset"]:
        proxy.reset()
        print(proxy.status())
    elif args["quit"]:
        proxy.quit()
    else:
        print("Unknown command", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
