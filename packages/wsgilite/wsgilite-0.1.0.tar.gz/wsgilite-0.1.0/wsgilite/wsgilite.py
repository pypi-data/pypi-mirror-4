#! /usr/bin/env python

try:
    execfile
except NameError:
    import inspect

    def execfile(file, globals=None, locals=None):
        frame = None
        try:
            if globals is None and locals is None:
                frame = inspect.stack()[-2][0]
                globals = frame.f_globals
                locals = frame.f_locals
            elif globals is not None and locals is None:
                locals = globals
            elif globals is None and locals is not None:
                frame = inspect.stack()[-2][0]
                globals = frame.f_globals
        finally:
            del frame
        with open(file, "r") as fh:
            exec(fh.read() + "\n", globals, locals)

import ast
import time
import logging
import wsgiref.simple_server
import argparse
import threading

import autoreloader

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-p', '--port', type=int, default=8000)
PARSER.add_argument('-a', '--address', type=str, default='')
PARSER.add_argument('-t', '--threads', type=int, default=10)
PARSER.add_argument('-r', '--autoreload', default=False, action='store_true')

PARSER.add_argument('--quiet', '-q',
                    default=logging.ERROR,
                    help='set log verbosity',
                    dest='loglevel',
                    action='store_const',
                    const=logging.CRITICAL)
PARSER.add_argument('--verbose', '-v',
                    dest='loglevel',
                    action='store_const',
                    const=logging.INFO)
PARSER.add_argument('--debug', '-d',
                    dest='loglevel',
                    action='store_const',
                    const=logging.DEBUG)
PARSER.add_argument('--logfile', dest='logfile', default=None)

PARSER.add_argument('app')


class AppMaker(object):
    """
    defers app loading until first request.
    """

    def __init__(self, app_string, autoreload=False):
        path, expr = app_string.split(':', 1)
        ast.parse(expr, 'app', mode='eval')
        self.app_string = app_string
        self._autoreload = autoreload
        self._lock = threading.Lock()

    @property
    def app(self):
        try:
            return self._application
        except AttributeError:
            with self._lock:
                # check *again* with the lock
                if hasattr(self, '_application'):
                    app = self._application
                else:
                    path, expr = self.app_string.split(':', 1)
                    try:
                        evalcontext = __import__(path, fromlist=['']).__dict__
                    except ImportError:
                        evalcontext = {'__name__': path}
                        execfile(path, evalcontext)
                        if self._autoreload:
                            autoreloader.assassinate([path])
                    self._application = app = eval(expr, evalcontext)
                return app

    def __call__(self, environ, start_response):
        app = self.app
        return app(environ, start_response)


def main():
    args = PARSER.parse_args()

    logging.basicConfig(filename=args.logfile, level=args.loglevel)
    if args.autoreload:
        autoreloader.assassinate([__file__])
    address = args.address
    port = args.port
    nthreads = max(1, args.threads)

    application = AppMaker(args.app, args.autoreload)
    if not args.autoreload:
        application = application.app

    server = wsgiref.simple_server.make_server(address, port, application)
    threads = [threading.Thread(target=server.serve_forever)
               for dummy in range(nthreads)]
    for thread in threads:
        thread.daemon = True
        thread.start()
    # don't join threads!
    print("Serving %r http://%s" % (server.application,
                                    "%s:%d" % server.server_address))

    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        print()
        print("Caught KeyboardInterrupt, bye!")
        return

if __name__ == '__main__':
    main()
