from nose import SkipTest
from nose.tools import assert_raises
from flask.app import Flask
try:
    from flask import __version__ as FLASK_VERSION
except ImportError:
    FLASK_VERSION = '0.6'
from webassets.test import TempEnvironmentHelper as BaseTempEnvironmentHelper
from flask.ext.assets import Environment

try:
    from flask import Blueprint
    Module = None
except ImportError:
    # Blueprints only available starting with 0.7,
    # fall back to old Modules otherwise.
    Blueprint = None
    from flask import Module


__all__ = ('TempEnvironmentHelper', 'Module', 'Blueprint')


class TempEnvironmentHelper(BaseTempEnvironmentHelper):

    def _create_environment(self, **kwargs):
        if FLASK_VERSION < '0.7':
            # Older Flask versions do not support the
            # static_folder argument, which we need to use
            # a temporary folder for static files, without
            # having to do sys.path hacking.
            raise SkipTest()

        if not hasattr(self, 'app'):
            self.app = Flask(__name__, static_folder=self.tempdir, **kwargs)
        self.env = Environment(self.app)
        return self.env


try:
    from test.test_support import check_warnings
except ImportError:
    # Python < 2.6
    import contextlib

    @contextlib.contextmanager
    def check_warnings(*filters, **kwargs):
        # We cannot reasonably support this, we'd have to copy to much code.
        # (or write our own). Since this is only testing warnings output,
        # we might slide by ignoring it.
        yield
