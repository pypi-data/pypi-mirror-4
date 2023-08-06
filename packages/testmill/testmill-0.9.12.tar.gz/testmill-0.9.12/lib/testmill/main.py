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

from __future__ import absolute_import, print_function

import sys
import logging
import textwrap
import traceback

from testmill import argparse, console, ravello, error, _version
from testmill.state import env


usage = textwrap.dedent("""\
    Usage: ravtest [-u <user>] [-p <password>] [-s <service_url>] [-q] [-v]
                   [-d] [-y] [-m <manifest>] <command> [OPTION]...
           ravtest --help [<command>]
           ravtest --version
""")

description = textwrap.dedent("""\
    Ravello TestMill, a system test driver for Ravello.

    The available options are:
        -u <user>, --user <user>
            Specifies the Ravello user name
        -p <password>, --password <password>
            Specifies the Ravello password
        -s <service_url>, --service-url <service_url>
            Specifies the Ravello API service URL
        -q, --quiet
            Be quiet
        -v, --verbose
            Be verbose
        -d, --debug
            Show debugging information
        -y, --yes
            Do not ask for confirmation
        -m, --manifest
            Use a different manifest
        -h, --help
            Show help and exit
        -V, --version
            Show version and exit

    The available commands are:
        login       log in to Ravello
        logout      log out from Ravello
        ps          show applications or blueprints
        run         run a remote command
        ssh         connect to an application
        save        save an application to a blueprint
        restore     restore an appliation from a blueprint
        clean       clean up applications or blueprints
        lint        check a project manifest

    Use 'ravtest <command> --help' to get help for a command.
    """)


from testmill import (command_login, command_ps, command_lint,
                      command_logout, command_run, command_ssh,
                      command_save, command_restore, command_clean)

subcommands = {
    'login': (command_login.do_login, command_login.add_args),
    'logout': (command_logout.do_logout, command_logout.add_args),
    'ps': (command_ps.do_ps, command_ps.add_args),
    'run': (command_run.do_run, command_run.add_args),
    'ssh': (command_ssh.do_ssh, command_ssh.add_args),
    'lint': (command_lint.do_lint, command_lint.add_args),
    'save': (command_save.do_save, command_save.add_args),
    'restore': (command_restore.do_restore, command_restore.add_args),
    'clean': (command_clean.do_clean, command_clean.add_args)
}


def create_parser():
    """Create command-line parser."""
    if sys.platform.startswith('win'):
        sys.argv[0] = sys.argv[0].rstrip('-script.py')
    parser = argparse.ArgumentParser(usage=usage, description=description,
                                     add_help=False)
    parser.add_argument('-u', '--user')
    parser.add_argument('-p', '--password')
    parser.add_argument('-s', '--service-url')
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-y', '--yes', action='store_true')
    parser.add_argument('-m', '--manifest')
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument('subcmd')
    return parser


def parse_args(parser, argv=None):
    """Parse aguments."""
    # Parse general arguments, extract the command, add command-specific
    # arguments, and then re-parse everything again.
    # The argparse module provides subparser support, and we could have
    # used that. However, there a serious usability issue with that, because
    # "command <subcmd> --foo" is an error if --foo is a valid argument
    # for command but not for the sub-command. Given that is very common
    # to mistakenly pass options out of order, we imlement our own solution
    # here that accepts the options in this case.
    try:
        args = parser.parse_args(argv)
    except argparse.ParseError as e:
        args = e.namespace
        if not (args.help or args.version) and not args.subcmd:
            console.write_err(parser.format_usage())
            console.error(str(e))
            error.exit(error.EX_USAGE)
    if args.help and not args.subcmd:
        console.write_err(parser.format_help())
        error.exit(error.EX_OK)
    if args.version and not args.subcmd:
        console.writeln_err(_version.version_string)
        error.exit(error.EX_OK)
    subcmd = args.subcmd
    if subcmd not in subcommands:
        console.error("Unknown command: '{0}'.", subcmd)
        error.exit(error.EX_USAGE)
    add_args = subcommands[subcmd][1]
    add_args(parser)
    try:
        args = parser.parse_args(argv)
    except argparse.ParseError as e:
        args = e.namespace
        if not args.help:
            console.write_err(parser.format_usage())
            console.error(str(e))
            error.exit(error.EX_USAGE)
    if args.help:
        console.write_err(parser.format_help())
        error.exit(error.EX_OK)
    return args


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
    env.api = ravello.RavelloClient(env.username, env.password, env.service_url)


def setup_logging():
    """Set up logging."""
    logger = logging.getLogger('testmill')
    if getattr(logger, '_testmill_configured', False):
        return
    logger.setLevel(logging.DEBUG if env.debug and env.verbose
                    else logging.INFO)
    handler = logging.StreamHandler(console)
    template = '%(levelname)s %(name)s: %(message)s'
    handler.setFormatter(logging.Formatter(template))
    logger.addHandler(handler)
    logger._testmill_configured = True


def main(argv=None):
    """The "ravtest" main entry point."""
    if sys.platform.startswith('win'):
        console.error('Windows is not currently supported by "ravtest".\n'
                      'Please use the Fabric front-end.')
        error.exit(1)
    parser = create_parser()
    args = parse_args(parser, argv)
    create_environment(args)
    setup_logging()
    command = subcommands[args.subcmd][0]
    try:
        ret = command(args, env)
    except KeyboardInterrupt:
        console.complete_partial_line()
        console.writeln('Exiting at user request.')
        ret = error.EX_INTERRUPTED
    except SystemExit as e:
        console.complete_partial_line()
        if env.debug:
            console.error('SystemExit caught')
            lines = traceback.format_exception(*sys.exc_info())
            console.writeln_err('Raised from:')
            console.writeln_err(''.join(lines))
        ret = e[0]
    except Exception as e:
        console.complete_partial_line()
        console.error(str(e))
        if env.debug:
            lines = ['An uncaught exception occurred:']
            lines += traceback.format_exception(*sys.exc_info())
            console.writeln_err()
            console.writeln_err(''.join(lines))
            console.writeln_err('Environment: {!r}'.format(env))
        ret = getattr(e, 'exitstatus', error.EX_SOFTWARE)
    return ret


if __name__ == '__main__':
    sys.exit(main())
