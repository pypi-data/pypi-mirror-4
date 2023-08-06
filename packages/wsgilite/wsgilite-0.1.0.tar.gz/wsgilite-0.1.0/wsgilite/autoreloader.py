#! /usr/bin/env python
try:
    import __builtin__ as builtins
    assert builtins  # silence pyflakes
except ImportError:
    import builtins

try:
    basestring
except NameError:
    basestring = unicode = str

import inspect
import logging
import os
import sys
import threading
import time

#TODO: Add the funny game/rpg elements back
#TODO: Add syntax checking
#TODO: use inotify instead of stat (where available)
#TODO: trim python std libs (optionally?)

__all__ = ['assassinate']
LOGGER = logging.getLogger(__name__)


def guesswatchfile(thing):
    if inspect.ismodule(thing):
        try:
            thingsourcefile = inspect.getsourcefile(thing)
            if not os.path.exists(thingsourcefile):
                raise TypeError("not really a file", thingsourcefile)
            return thingsourcefile

        except TypeError:
            LOGGER.debug("cannot watch %r, no source file", thing)
            return None
    if thing in sys.modules:
        return guesswatchfile(sys.modules[thing])
    elif isinstance(thing, basestring) and os.path.exists(thing):
        return thing
    raise ValueError("Couldn't figure out what to watch", thing)


def check_syntax(path):
    try:
        compile(open(path).read(), path, "exec")
        return True
    except SyntaxError:
        LOGGER.exception("target did not compile %r", path)
        return os.path.splitext(path, '.py')


def restart_execl(argv=list(sys.argv),
                  closerange=(3, 1000)):
    LOGGER.debug("restart_execl(%r, %r)", argv, closerange)
    os.closerange(*closerange)
    os.execl(argv[0], *argv),


def assassinate(watch_files,
                sleep_time=1,
                restart=restart_execl,
                _reentry=[],
                _real_watchfiles={},
                _lock=threading.Lock()):

    # watch some files
    with _lock:
        for watch_thing in watch_files:
            LOGGER.debug("assasinate(%r)", watch_thing)
            watch = guesswatchfile(watch_thing)
            if watch is None or watch in _real_watchfiles:
                continue
            LOGGER.debug("watching %s", watch)
            _real_watchfiles[watch] = os.stat(watch).st_mtime

        # if this has been called before, bail out
        if _reentry:
            return
        _reentry.append(True)

    # monkey patch imports
    real_import = builtins.__import__

    def assassin_import(name, globals={}, locals={}, fromlist=[], level=-1):
        peek_keys = sys.modules.keys()
        importedModule = real_import(name, globals, locals, fromlist, level)
        if importedModule.__name__ not in peek_keys:
            assassinate([importedModule])
        return importedModule

    LOGGER.debug("replacing __builtin__.__import__")
    builtins.__import__ = assassin_import

    def assassin():
        while True:
            with _lock:
                for watch, mtime in _real_watchfiles.items():
                    # retry a couple times in case the file is being moved
                    # about non-atomically
                    for tries in range(2, -1, -1):
                        try:
                            new_mtime = os.stat(watch).st_mtime
                            if new_mtime != mtime:
                                LOGGER.info("Restarting on file change, %r", watch)
                                if check_syntax(watch):
                                    restart()
                                else:
                                    _real_watchfiles[watch] = new_mtime
                        except OSError:
                            if tries:
                                time.sleep(0.3)
                            else:
                                raise

            time.sleep(sleep_time)

    athread = threading.Thread(target=assassin)
    athread.daemon = True
    athread.start()
