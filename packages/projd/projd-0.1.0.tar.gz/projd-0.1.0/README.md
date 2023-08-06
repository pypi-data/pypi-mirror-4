
## Introduction


This idea is inspired by Git and Django, which assume projects are organized
within a directory.  Many other applications and projects work this way, like
Ruby on Rails and Maven.

Many projects, like source code repositories, web applications, etc., store
locations of code, configuration, scripts, virtual environments, etc., relative
to the root directory of the project or application.

When a script, application, executable, binary, program, or command is
executed, it needs to find the root directory of the project it is supposed to
operate on.  For example, `git status` only works when called from within
a git repository.  Alternatively, a Django `manage.py` script can be run from
anywhere, yet it knows to operate on the web application it is located within.

There are two sub-organizing principles seen in project commands, based around
how they find the root directory of the project:

- In the "cwd" approach, exemplified by `git`, code and executables find the
  project based on the current working directory.  For example, to work in a
  git repository, one must first `cd` to somewhere in the repository directory
  tree.
- In the "which" approach, exemplified by a django `manage.py` script, code and
  executables find the project based on the path of the executable itself.  For
  example, a django `manage.py` script expects to be located in the root of
  the project.

An advantage of the "cwd" approach is that one set of binaries can be used
with multiple projects.

An advantages of the "which" approach are that one can run the binaries from
anywhere.  Another advantage is that a different version of code/binaries can
be associated with each project.  This can be useful for deployments of
multiple version of an application.


## Contribute

Feel free to make a pull request on github.


## Requirements

- Probably Python 2.7 (since that is the only version it has been tested with.)


## Installation


### Install from pypi.python.org

Download and install using pip:

    pip install projd


### Install from github.com

Using github, one can clone and install a specific version of the package:

    cd ~
    git clone git@github.com:todddeluca/projd.git
    cd projd
    python setup.py install

Or use pip:

    pip install git+git://github.com/todddeluca/projd.git#egg=projd


## Usage

There are two functions for finding the root directory of a project based on
that root directory containing a specific token, a file or directory.  One
function works based on the current working directory.  

For example to find the root directory of a git repository one would do:

    import projd
    root = projd.cwd_token_dir('.git')

To find the root directory of a project containing the script being executed
(similar to how a django manage.py file works), one would do:

    import projd
    root = projd.script_token_dir('.git')




