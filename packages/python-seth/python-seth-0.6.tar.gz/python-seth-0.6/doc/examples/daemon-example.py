#!/usr/bin/env python

import sys, time
from seth import Daemon

class MyDaemon(Daemon):

    def __init__(self, pid, log):
      Daemon.__init__(self, pid, stdout=log, stderr=log)

    def run(self):
        """Overrides Daemon().run() with actions you want to daemonize.
        MyDaemon.run() is then called within MyDaemon().start()"""
        print('Starting Deamon!')  # message issued on self.stdout
        while True:
            time.sleep(1)
            sys.stderr.write('œ unicode write test to stderr\n')
            sys.stdout.write('write test to stdout\n')

    def shutdown(self):
        """Overrides Daemon().shutdown() with some clean up"""
        print("Stopping Daemon!")  # message issued on self.stdout

if __name__ == '__main__':
    daemon = MyDaemon('/tmp/daemon-example.pid',
            '/tmp/daemon.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print('Unknown command')
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: {} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)
