Cdiff
=====

.. image:: https://travis-ci.org/ymattw/cdiff.png?branch=master
   :target: https://travis-ci.org/ymattw/cdiff
   :alt: Build status

Term based tool to view **colored**, **incremental** diff in *Git/Mercurial/Svn*
workspace or from stdin, with **side by side** and **auto pager** support.
Requires python (>= 2.5.0) and ``less``.

.. image:: http://ymattw.github.com/cdiff/img/default.png
   :alt: default
   :align: center

.. image:: http://ymattw.github.com/cdiff/img/side-by-side.png
   :alt: side by side
   :align: center
   :width: 900 px

Installation
------------

Install with pip
~~~~~~~~~~~~~~~~

Cdiff is already listed on `PyPI <http://pypi.python.org/pypi/cdiff>`_, you can
install with ``pip`` if you have the tool.

.. code:: sh
 
    pip install --upgrade cdiff

Install with setup.py
~~~~~~~~~~~~~~~~~~~~~

You can also run the setup.py from the source if you don't have ``pip``.

.. code:: sh

    git clone https://github.com/ymattw/cdiff.git
    cd cdiff
    ./setup.py install

Download directly
~~~~~~~~~~~~~~~~~

Just save `cdiff.py <https://raw.github.com/ymattw/cdiff/master/cdiff.py>`_ to
whatever directory which is in your ``$PATH``, for example, ``$HOME/bin`` is in
my ``$PATH``, so I save the script there and name as ``cdiff``.

.. code:: sh

    curl -ksS https://raw.github.com/ymattw/cdiff/master/cdiff.py > ~/bin/cdiff
    chmod +x ~/bin/cdiff

Usage
-----

Show usage:

.. code:: sh

    cdiff -h

Read diff from local modification in a *Git/Mercurial/Svn* workspace:

.. code:: sh

    cd proj-workspace
    cdiff                       # view colored incremental diff
    cdiff -s                    # view side by side
    cdiff -s -w 90              # use text width 90 other than default 80
    cdiff -s file1 dir2         # view modification of given files/dirs only

Read the log with changes (e.g. ``git log -p``, ``svn log --diff``) in a
*Git/Mercurial/Svn* workspace (note *--diff* option is new in svn 1.7.0):

.. code:: sh

    cd proj-workspace
    cdiff -l
    cdiff -ls                   # equivalent to cdiff -l -s
    cdiff -ls -w90
    cdiff -ls file1 dir2        # see log with changes of given files/dirs only

Pipe in a diff:

.. code:: sh

    git log -p -2 | cdiff -s    # view git log with changes of last 2 commits
    git show 15bfa | cdiff -s   # view a git commit
    svn diff -r1234 | cdiff -s  # view svn diff comparing to given revision
    cdiff < foo.patch           # view a patch file (unified format only)
    cat foo.patch | cdiff       # same as above
    diff -u foo bar | cdiff     # pipe in diff between two files (note the '-u')
    diff -ur dir1 dir2 | cdiff  # pipe in diff between two dirs

Redirect output to another patch file is safe:

.. code:: sh

    svn diff -r PREV | cdiff -s > my.patch

Notes
-----

- Verified on `travis <https://travis-ci.org/ymattw/cdiff>`_ with python 2.5,
  2.6, 2.7, 3.2, 3.3 and pypy
- Only takes unified diff for input
- Side by side mode has alignment problem for wide chars
- Pull requests are very welcome, run ``make test`` to verify (required tool
  *coverage* can be installed with ``pip install coverage``)

See also
--------

I have another tool `coderev <https://github.com/ymattw/coderev>`_ which
generates side-by-side diff pages for code review from two given files or
directories, I found it's not easy to extend to support git so invented
`cdiff`.  Idea of ansi color markup is also from project `colordiff
<https://github.com/daveewart/colordiff>`_.

