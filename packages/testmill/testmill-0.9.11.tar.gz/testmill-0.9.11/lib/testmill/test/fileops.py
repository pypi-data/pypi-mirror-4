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
import textwrap

__all__ = ('chdir', 'mkdir', 'mkfile', 'touch', 'text')


class chdir(object):

    def __init__(self, dirname):
        self.dirname = dirname

    def __enter__(self):
        self.oldpwd = os.getcwd()
        os.chdir(self.dirname)

    def __exit__(self, *exc_info):
        os.chdir(self.oldpwd)


class mkdir(object):

    def __init__(self, dirname):
        self.dirname = dirname

    def __enter__(self):
        self.oldpwd = os.getcwd()
        os.mkdir(self.dirname)
        os.chdir(self.dirname)

    def __exit__(self, *exc_info):
        os.chdir(self.oldpwd)


def mkfile(fname, contents=''):
    with open(fname, 'w') as fout:
        fout.write(contents)

touch = mkfile

text = textwrap.dedent
