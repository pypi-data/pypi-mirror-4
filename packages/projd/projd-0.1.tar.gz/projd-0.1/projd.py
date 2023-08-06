'''
The 'd' in projd stands for directory.  Project based helper functions.  A
project is a group of files and directories within a common root dir.  This
module contains functions for finding the root directory, etc.

There are two sub-organizing principles seen in projects, based around how they
find the root directory of the project:

- In the "cwd" approach, exemplified by `git`, code and executables find the
  project based on the current working directory.  For example, to work in a
  git repository, one must first `cd` somewhere into the repository directory
  (or a subdir).
- In the "which" approach, exemplified by a django `manage.py` script, code and
  executables find the project based on the path of the executable itself.  For
  example, a django `manage.py` script expects to be located in the root of
  the.project.

The advantage to the "cwd" approach is that one set of binaries can be used
with multiple projects.

The advantages of the "which" approach are that one can run the binaries from
anywhere and that a different version of code/binaries can be associated with
each project.
'''

import os
import sys


#############################
# PROJECT DIRECTORY FUNCTIONS

def cwd_token_dir(token):
    '''
    Find the directory containing token, starting from the current working 
    directory.

    Start walking up the directory tree from the current working directory and
    return the first directory found that contains a filename, dirname, or
    linkname that matches token.  If no directory is found containing token,
    return None.

    :param token: a path basename.
    '''
    return token_dir(cwd_dir(), token)


def script_token_dir(token):
    '''
    Find the directory containing token, starting from the location of the
    running script.

    Start walking up the directory tree from the location of the currently
    running script (as indicated by sys.argv[0]) and return the first directory
    found that contains a filename, dirname, or linkname that matches token.
    If no directory is found containing token, return None.

    :param token: a path basename.
    '''
    return token_dir(script_dir(), token)


#####################
# AUXILIARY FUNCTIONS


def token_dir(path, token):
    '''
    Find the directory containing token, starting from path.

    Start walking up the directory tree from path and return the first 
    directory found that contains a filename, dirname, or linkname that matches
    token.  If no directory is found containing token, return None.

    :param path: a path at which to start searching for a directory containing
    token.
    :param token: a path basename.
    '''
    # make sure that token does not contain any directories.
    basename = os.path.basename(token)
    for d in walk_up(path):
        if os.path.exists(os.path.join(d, basename)):
            return d

    return None


def script_dir(realpath=False):
    '''
    Return the script directory from sys.argv[0] as an absolute path using
    os.path.abspath (default) or os.path.realpath (if realpath is True).
    '''
    d = os.path.dirname(sys.argv[0])
    if realpath:
        return os.path.realpath(d)
    else:
        return os.path.abspath(d)


def cwd_dir(realpath=False):
    '''
    Return the current working directory as an absolute path using
    os.path.abspath (default) or os.path.realpath (if realpath is True).
    Note that although the docs do not explicitly say so, os.getcwd() might
    already return a real or absolute path, so this function might be
    redundant.
    '''
    d = os.getcwd()
    if realpath:
        return os.path.realpath(d)
    else:
        return os.path.abspath(d)


def walk_up(path, realpath=False):
    '''
    First normalize path using os.path.expanduser, then os.path.abspath
    (default) or os.path.realpath (if realpath is True).  Then yield path and
    every directory above path.

    Example:

        list(walk_up('~/tmp/./')) -> 
        ['/Users/td23/tmp', '/Users/td23', '/Users', '/']

    path: Should be a directory.
    '''
    if realpath:
        curdir = os.path.realpath(os.path.expanduser(path))
    else:
        curdir = os.path.abspath(os.path.expanduser(path))

    while 1:
        yield curdir
        curdir, tail = os.path.split(curdir)
        if not tail:
            break


def which(program):
    '''
    In python3.3, see shutil.which().  Emulate unix 'which' command.  If program
    contains any directories (e.g. './foo'), return program, else if program is
    found on the PATH, return the absolute path to it, otherwise return None.
    http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
    '''
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


