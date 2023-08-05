import signal
import threading
import code
import time
import random
import tempfile
import socket
import os

i = 0

print os.getpid()

# possibly like twisted.manhole?
# see #12403 and discussion. Suggests overwriting stdout/stderr
# ultimately.
# might be nice if this spawned a new 'debug thread' on accept
# rather than on a signal; would allow re-attaching (just do an
# listen(1) / accept() / interact loop)
# perhaps a sys.displayhook (see pep 217) which recognises where
# it has been called from ?

class DebugConsole(code.InteractiveConsole):

    def __init__(self, *o, **k):
        self.__sock_path = os.path.join(tempfile.mkdtemp(),
                                        str(os.getpid()))
        print self.__sock_path
        self.__sock = socket.socket(socket.AF_UNIX,
                                    socket.SOCK_STREAM)
        self.__sock.bind(self.__sock_path)
        self.__sock.listen(1)
        self.__conn = self.__sock.accept()[0]
        self._debug_handle = self.__conn.makefile('rw')
        code.InteractiveConsole.__init__(self, *o, **k)

    def write(self, data):
        if data:
            self._debug_handle.write(data)
            self._debug_handle.flush()

    def raw_input(self, prompt=''):
        self.write(prompt)
        return self._debug_handle.readline()


def new_debug():
    context = globals()
    context['console_context'] = DebugConsole(context)
    context['console_context'].interact()


def handler(signum, frame):
    t = threading.Thread(target=new_debug)
    t.daemon = True
    t.start()


def run():
    global i
    while True:
        time.sleep(random.random())
        i += 1


if __name__ == '__main__':
    signal.signal(signal.SIGUSR2, handler)
    run()
