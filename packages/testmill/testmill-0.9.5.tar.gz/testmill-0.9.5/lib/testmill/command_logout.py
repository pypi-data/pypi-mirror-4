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

import textwrap
from testmill import console, login


usage = textwrap.dedent("""\
        usage: ravtest [OPTION]... logout
               ravtest logout --help
        """)

description = textwrap.dedent("""\
        Log out from the Ravello Service.
        """)


def add_args(parser):
    """Add command-line options for "ravello login"."""
    parser.usage = usage
    parser.description = description


def do_logout(args, env):
    """The "ravello logout" command."""
    login.remove_token()
    console.info('Logged out.')
    return 0
