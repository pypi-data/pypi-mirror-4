# Copyright 2012-2013 Ravello Systems, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import tempfile
import shutil
import argparse

from nose import SkipTest
from testmill.ravello import RavelloClient
from testmill.state import env, _Environment

testenv = _Environment()
from testmill.test import networkblocker, sudo
from testmill.test.fileops import *

if sys.version_info[0] == 3:
    import configparser
else:
    import ConfigParser as configparser


__all__ = ('testenv', 'require_sudo', 'require_network_blocking',
           'TestSuite', 'unittest', 'integrationtest', 'systemtest',
           'tempdir', 'get_common_args', 'parse_ps_output', 'environ')


testdir, _ = os.path.split(os.path.abspath(__file__))
parent = testdir
for i in range(3):
    parent, _ = os.path.split(parent)
topdir = parent


def setup_package():
    # Have nose capture stderr too.
    testenv._nose_saved_stderr = sys.stderr
    sys.stderr = sys.stdout

def teardown_package():
    sys.stderr = testenv._nose_saved_stderr
    testenv._nose_saved_stderr = None


# Create an environment based on ~/test.cfg.

def create_test_environment():
    """Create at test environment based on $topdir/test.cfg."""
    fname = os.path.join(topdir, 'test.cfg')
    if not os.access(fname, os.R_OK):
        m = 'Tests need to be run from a checked out source repository.'
        raise RuntimeError(m)
    config = configparser.ConfigParser()
    config.read([fname])
    def config_var(name, default=None):
        try:
            return config.get('test', name)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    testenv.username = config_var('username')
    testenv.password = config_var('password')
    testenv.service_url = config_var('service_url') or RavelloClient.default_url
    testenv.network_blocking = config_var('network_blocking')
    testenv.sudo_password = config_var('sudo_password')
    testenv.topdir = topdir
    testenv.testdir = testdir

# Create the test environment here. A single copy is shared by all tests.

create_test_environment()


# method decorators

def require_sudo(func):
    def wrapped(*args, **kwds):
        if not sudo.have_sudo():
            raise SkipTest('sudo is not available')
        if testenv.sudo_password:
            if not sudo.check_sudo_password(testenv.sudo_password):
                raise SkipTest('incorrect sudo_password in test.cfg')
        elif not sudo.check_passwordless_sudo():
            raise SkipTest('sudo_password not set in test.cfg')
        return func(*args, **kwds)
    wrapped.__name__ = func.__name__
    return wrapped

def require_network_blocking(func):
    def wrapped(*args, **kwds):
        if not networkblocker.have_blocker():
            raise SkipTest('network blocking is not available')
        if not testenv.network_blocking:
            raise SkipTest('network blocking disabled in test.cfg')
        return require_sudo(func)(*args, **kwds)
    wrapped.__name__ = func.__name__
    return wrapped


# utilities

def tempdir():
    dname = tempfile.mkdtemp()
    testenv._tempdirs.append(dname)
    return dname


def rmtree(dname):
    def paranoia_ok(dname):
        if '/..' in dname or '\\..' in dname:
            return False
        return '/tmp/' in dname or '\\temp\\' in dname
    # Refuse to remove directories that are not in a common temp
    # directory. This check is just for peace of mind, it should
    # never fail. In platforms with uncommon temp directories this
    # check may result in a temp directory not being cleaned up.
    if paranoia_ok(dname):
        try:
            shutil.rmtree(dname)
        except OSError:
            # On Windows a WindowsError is raised when files are
            # still open
            pass


def parse_ps_output(output):
    """Parse the output of `ravtest ps` and return a list of
    (project, application, running) tuples.
    """
    result = []
    project = app = info = None
    for line in output.splitlines():
        line = line.strip()
        if not line and app:
            result.append((project, app, info))
            app = None
            continue
        if line.startswith('== '):
            project = line[line.find(':')+3:-1]
        elif line.startswith('=== '):
            app = line[line.find(':')+3:-1]
            info = {}
        if not app:
            continue
        if 'VMs' in line:
            info['vms'] = int(line.split()[0])
    return result


def get_common_args():
    """Return a list with the common command-line options."""
    args = ['-u', testenv.username, '-p', testenv.password,
            '-s', testenv.service_url]
    return args


class environ(object):
    """Context manager to manage os.environ."""

    def __init__(self, **env):
        self.env = env
        self.restore = {}

    def __enter__(self):
        for key in self.env:
            self.restore[key] = os.environ[key]
            os.environ[key] = self.env[key]

    def __exit__(self, *exc_info):
        for key in self.restore:
            os.environ[key] = self.restore[key]
        self.restore.clear()


# This is a copy of main.create_environment(). This allows us
# to run unittests and some integration tests already on Py3k.
# (Fabric doesn't yet support Py3k)

def create_environment(args):
    """Set up the global environment."""
    env.username = args.user
    env.password = args.password
    env.service_url = args.service_url
    env.quiet = args.quiet
    env.verbose = args.verbose
    env.manifest = args.manifest
    env.debug = args.debug
    env.always_confirm = args.yes
    env.args = args
    env.api = RavelloClient(env.username, env.password, env.service_url)


class TestSuite(object):
    """Base for test suites."""

    @classmethod
    def setup_class(cls):
        os.chdir(testenv.testdir)

    def setup(self):
        unittest = getattr(self, 'unittest', False)
        integrationtest = getattr(self, 'integrationtest', False)
        systemtest = getattr(self, 'systemtest', False)
        if integrationtest or systemtest:
            if not testenv.username or not testenv.password:
                raise SkipTest('This test requires API credentials.')
        testenv._tempdirs = []
        testenv.tempdir = tempdir()
        testenv._saved_stderr = sys.stderr 
        sys.stderr = sys.stdout  # Have nose capture stderr too
        testenv.context = env.new()
        testenv.context.__enter__()
        if integrationtest:
            args = argparse.Namespace(
                        user = testenv.username,
                        password = testenv.password,
                        service_url = testenv.service_url,
                        manifest = None,
                        quiet = False, verbose=True,
                        debug = True, yes = False)
            create_environment(args)
            env.api._login()

    def teardown(self):
        testenv.context.__exit__()
        sys.stderr = testenv._saved_stderr
        for dname in testenv._tempdirs:
            rmtree(dname)
        del testenv._tempdirs[:]


def unittest(obj):
    """A suite of unit tests.

    Each unit tests get a new empty env.
    Run all unit tests with "nosetests -a unittest".
    """
    obj.unittest = True
    return obj

def integrationtest(obj):
    """A suite of integration tests.

    Each test get a new and fully configured env.
    Run all integration tests with "nosetests -a integrationtest".
    """
    obj.integrationtest = True
    return obj

def systemtest(obj):
    """A suite of system tests.

    Each test gets a new empty env. The test will bootstrap the env
    through its command-line arguments.
    """
    obj.systemtest = True
    return obj
