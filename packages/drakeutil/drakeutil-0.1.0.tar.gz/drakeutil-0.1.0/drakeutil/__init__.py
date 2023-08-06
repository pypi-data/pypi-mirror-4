# -*- coding: utf-8 -*-
#
#  __init__.py
#  drakeutil
#

"""
Helpers for Drake workflows.
"""

from shutil import copy, move, copytree, rmtree  # noqa
from os import environ, path, rename, stat  # noqa
from datetime_tz import datetime_tz
from contextlib import contextmanager, closing

import subprocess


# set up special drake environment variables
for k in environ:
    if k.startswith('INPUT') or k.startswith('OUTPUT'):
        locals()[k] = environ[k]

# these special variables should always be lists
INPUTS = locals().get('INPUTS', '').split()
OUTPUTS = locals().get('OUTPUTS', '').split()


def hdfs_timestamp(filename):
    "When was this file last modified?"
    stdout, stderr = subprocess.Popen(['hadoop', 'fs', '-stat', filename],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if not stdout and 'No such' in stderr:
        return None

    return datetime_tz.smartparse(stdout)


def hdfs_exists(filename):
    "Does this file or directory exist?"
    p = subprocess.Popen(['hadoop', 'fs', '-test', '-e', filename])
    p.communicate()
    return p.returncode == 0


def file_timestamp(filename):
    "When was this file last modified?"
    try:
        return datetime_tz.utcfromtimestamp(stat(filename).st_mtime)
    except OSError:
        return

# optional MySQL support
try:
    import MySQLdb

    @contextmanager
    def mysql_cursor(host=None, port=3306, db=None, user=None, passwd=None):
        with closing(MySQLdb.connect(host=host, port=port, db=db, user=user,
                passwd=passwd)) as conn:
            with closing(conn.cursor()) as cursor:
                yield cursor

except ImportError:
    pass
