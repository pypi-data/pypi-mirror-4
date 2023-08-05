"""
Tattler, a nose plugin that tattles on functions.
"""
import os
import mock
import inspect
from importlib import import_module

from nose.plugins import Plugin


__all__ = ['Tattler']


class TattleTale(Exception):
    pass


class WatcherState(object):
    def __init__(self):
        self.active = False


class Watcher(object):
    """A watcher that complains when its function is called."""
    def __init__(self, path):
        # Use mock's importer to get a reference to the original
        patcher = mock.patch(path)
        self.func, _ = patcher.get_original()

        # Use a wrapper function as the patch so it can be bound
        def wrapper(*args, **kwargs):
            if self.active:
                raise TattleTale('{} called!'.format(path))
            else:
                return self.func(*args, **kwargs)

        # Actually patch the object this time
        self.patcher = mock.patch(path, new=wrapper)
        self.patcher.start()

        self.active = False

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def destroy(self):
        try:
            if len(self.patcher._active_patches):
                self.patcher.stop()
        except AttributeError:
            pass


class Tattler(Plugin):
    """The Tattler Plugin."""
    name = 'tattler'

    def __init__(self, *args, **kwargs):
        super(Tattler, self).__init__(*args, **kwargs)

        self._paths = []
        self._watchers = []

    # Nose plugin hooks

    def options(self, parser, env=os.environ):
        parser.add_option('-t', '--tattle-on', action='append',
                          dest='tattle_on')
        super(Tattler, self).options(parser, env=env)

    def configure(self, options, conf):
        super(Tattler, self).configure(options, conf)
        if not self.enabled:
            return

        self._paths = options.tattle_on

        if not self._paths:
            self.enabled = False

    def beforeImport(self, filename, module):
        # Init requires sys.path to be set by nose, so do this in beforeImport
        self.init()

    def finalize(self, result):
        self.destroy()

    def beforeTest(self, test):
        self.start()

    def afterTest(self, test):
        self.stop()

    # Plugin specific methods

    def watch(self, path):
        """Add a watcher for a path."""
        watcher = Watcher(path)

        self._watchers.append(watcher)

    def init(self):
        """Watch all paths."""
        for path in self._paths:
            self.watch(path)

    def start(self):
        """Start watchers."""
        for watcher in self._watchers:
            watcher.start()

    def stop(self):
        """Stop watchers."""
        for watcher in self._watchers:
            watcher.stop()

    def destroy(self):
        """Destroy watchers."""
        self.stop()
        for watcher in self._watchers:
            watcher.destroy()

        self._watchers = []
