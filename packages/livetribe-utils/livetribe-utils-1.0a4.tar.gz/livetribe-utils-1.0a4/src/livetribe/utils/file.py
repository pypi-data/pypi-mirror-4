#
# Copyright 2013 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import contextlib
from grp import getgrnam
import os
from pwd import getpwnam
import shutil
import tempfile


@contextlib.contextmanager
def temp_directory(*args, **kwargs):
    """
    Context manager returns a path created by mkdtemp and cleans it up afterwards.
    """

    path = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield path
    finally:
        shutil.rmtree(path)


def chown(path, username_or_uid=None, group_or_gid=None):
    """
      Change the owner and group id of path and all its contents

      :param path: The root path
      :param username_or_uid: A username or uid.  Defaults to uid of caller.
      :param group_or_gid: A group name or gid.  Defaults to gid of caller.
    """
    try:
        uid = int(username_or_uid)
    except ValueError:
        try:
            uid = getpwnam(username_or_uid).pw_uid
        except NameError:
            raise ValueError('%s does not exist' % username_or_uid)

    try:
        gid = int(group_or_gid)
    except (ValueError, TypeError):
        try:
            gid = getgrnam(group_or_gid).gr_gid
        except KeyError:
            raise ValueError('%s does not exist' % group_or_gid)

    for root, directories, files in os.walk(path):
        for d in directories:
            os.chown(os.path.join(root, d), uid, gid)
        for f in files:
            os.chown(os.path.join(root, f), uid, gid)


def chmod(path, file_mode=0644, directory_mode=0755):
    """
      Change the mode of path and all its contents

      :param path: The root path
      :param file_mode: The mode.  Defaults to 0644.
      :param directory_mode: The mode.  Defaults to 0755.
    """

    for root, directories, files in os.walk(path):
        for d in directories:
            os.chmod(os.path.join(root, d), directory_mode)
        for f in files:
            os.chmod(os.path.join(root, f), file_mode)

