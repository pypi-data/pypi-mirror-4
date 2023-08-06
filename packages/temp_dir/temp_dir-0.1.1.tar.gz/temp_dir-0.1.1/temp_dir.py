'''
Change into newly created temporary directory for executing a block of code.

Intended as a tool to ease "integration" testing.
'''

import tempfile
import shutil
import os
import functools
import contextlib


@contextlib.contextmanager
def in_temp_dir():
    ''' Change into a temporary directory for the duration of the block.

    On exit the original working directory is restored and the temporary
    directory is removed.

    with in_temp_dir():
        tempfile = open('tempfile', 'w')
        ...
    '''
    original_directory = os.getcwd()
    temporary_directory = tempfile.mkdtemp()
    os.chdir(temporary_directory)
    try:
        yield temporary_directory
    finally:
        try:
            os.chdir(original_directory)
        finally:
            shutil.rmtree(temporary_directory)


def within_temp_dir(func):
    ''' Make the decorated function execute in a temporary directory.

    Create & change into a temporary directory, when the decorated function
    is called.
    On exit the original working directory is restored and the temporary
    directory is removed.

    @within_temp_dir
    def f():
        tempfile = open('tempfile', 'w')
        ...
    '''

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        with in_temp_dir():
            return func(*args, **kwargs)

    return decorated
