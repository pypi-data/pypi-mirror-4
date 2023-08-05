##################
importfs extension
##################

Imports a set of files from a given file-system into a `Mercurial`_
repository as a changeset.

The development of this extension was paid for by `Lantiq`_. It was
written and released as Open Source by `Markus Zapke-Gründemann`_.

Repository: https://bitbucket.org/keimlink/hg-importfs

Issue tracker: https://bitbucket.org/keimlink/hg-importfs/issues

Python Package Index: http://pypi.python.org/pypi/hg-importfs

Mercurial wiki: http://mercurial.selenic.com/wiki/ImportfsExtension

Installation
============

It is assumed that you **already have Mercurial installed**. If not,
please do so first either by `downloading`_ and installing the
appropriate package for your operating system or by using `pip`_::

    $ pip install Mercurial

As a Python package
-------------------

The easiest way is to install the importfs extension is to use `pip`_::

    $ pip install hg-importfs

Using easy_install instead of pip is also possible::

    $ easy_install hg-importfs

Now add the extension to the extensions section in your
``.hgrc``/``mercurial.ini`` file::

    [extensions]
    importfs =

As a Mercurial repository
-------------------------

Instead of installing the Python package you can also clone the repository::

    $ hg clone https://bitbucket.org/keimlink/hg-importfs

To activate the extension you have to add the full path to
``importfs.py`` to your ``.hgrc``/``mercurial.ini`` file::

    [extensions]
    importfs = /path/to/hg-importfs/importfs.py

Usage
=====

After installing the extension you can use the following command to show
the full help including all options::

    $ hg help importfs

Example
=======

Assuming you have a project on your file system which has different
versions in different directories. Maybe because you never used a
version control system (VCS) for your project. Or maybe because there is
no convert extension available for the VCS you are using. In our
scenario the three versions of the project look like this::

    .
    ├── myproject-v1
    │   ├── LICENSE
    │   ├── README
    │   ├── doc
    │   │   ├── index.rst
    │   │   ├── start.rst
    │   │   └── widgets.rst
    │   └── src
    │       ├── cmdutils.py
    │       ├── dispatcher.py
    │       └── widgets.py
    ├── myproject-v2
    │   ├── LICENSE
    │   ├── README
    │   ├── doc
    │   │   ├── index.rst
    │   │   ├── start.rst
    │   │   └── widgets.rst
    │   └── src
    │       ├── cmdutils.py
    │       ├── dispatcher.py
    │       ├── resources.py
    │       └── widgets.py
    └── myproject-v3
        ├── LICENSE
        ├── README
        ├── doc
        │   ├── index.rst
        │   ├── start.rst
        │   └── widgets.rst
        └── src
            ├── dispatcher.py
            ├── resources.py
            └── widgets.py

Run the following command to import the first version of the project
into a Mercurial repository ``myrepo``. The repository does not exist so
it will be created for you::

    $ hg importfs myrepo myproject-v1
    created repository myrepo
    0 files updated, 0 files merged, 0 files removed, 0 files unresolved
    adding LICENSE
    adding README
    adding doc/index.rst
    adding doc/start.rst
    adding doc/widgets.rst
    adding src/cmdutils.py
    adding src/dispatcher.py
    adding src/widgets.py

Now you have a repository with one changeset. This changeset contains
all your files from ``myproject-v1``.

::

    $ hg log -R myrepo
    changeset:   0:60304fa41a49
    tag:         tip
    user:        Markus Zapke-Gründemann <markus@keimlink.de>
    date:        Tue Jul 10 10:19:10 2012 +0200
    summary:     importfs commit.

As you can see importfs created a commit message for you because you
didn't specify one for the first import.

The second import will put all the files from ``myproject-v2`` as a new
changeset on top of changeset 0. And this time we want to use our own
commit message and tag the changeset::

    $ hg importfs myrepo myproject-v2 -m "Second import." -t second_import
    8 files updated, 0 files merged, 0 files removed, 0 files unresolved
    adding src/resources.py

Now there are two new changesets::

    $ hg log -R myrepo
    changeset:   2:c8ff824da6c8
    tag:         tip
    user:        Markus Zapke-Gründemann <markus@keimlink.de>
    date:        Tue Jul 10 10:27:10 2012 +0200
    summary:     Added tag second_import for changeset 825c9a9356fd

    changeset:   1:825c9a9356fd
    tag:         second_import
    user:        Markus Zapke-Gründemann <markus@keimlink.de>
    date:        Tue Jul 10 10:27:10 2012 +0200
    summary:     Second import.

    changeset:   0:60304fa41a49
    user:        Markus Zapke-Gründemann <markus@keimlink.de>
    date:        Tue Jul 10 10:19:10 2012 +0200
    summary:     importfs commit.

Let's import the last version of the project into a new branch with
changeset 0 as parent::

    $ hg importfs myrepo myproject-v3 -m "Third import." -t third_import -b branch_2 -r 0
    8 files updated, 0 files merged, 1 files removed, 0 files unresolved
    marked working directory as branch branch_2
    (branches are permanent and global, did you want a bookmark?)
    removing src/cmdutils.py
    adding src/resources.py

The repository history looks now like this::

    $ hg glog -R myrepo
    @  changeset:   4:3ec5adb0448e
    |  branch:      branch_2
    |  tag:         tip
    |  user:        Markus Zapke-Gründemann <markus@keimlink.de>
    |  date:        Tue Jul 10 10:32:32 2012 +0200
    |  summary:     Added tag third_import for changeset bfcf48ac159e
    |
    o  changeset:   3:bfcf48ac159e
    |  branch:      branch_2
    |  tag:         third_import
    |  parent:      0:60304fa41a49
    |  user:        Markus Zapke-Gründemann <markus@keimlink.de>
    |  date:        Tue Jul 10 10:32:32 2012 +0200
    |  summary:     Third import.
    |
    | o  changeset:   2:c8ff824da6c8
    | |  user:        Markus Zapke-Gründemann <markus@keimlink.de>
    | |  date:        Tue Jul 10 10:27:10 2012 +0200
    | |  summary:     Added tag second_import for changeset 825c9a9356fd
    | |
    | o  changeset:   1:825c9a9356fd
    |/   tag:         second_import
    |    user:        Markus Zapke-Gründemann <markus@keimlink.de>
    |    date:        Tue Jul 10 10:27:10 2012 +0200
    |    summary:     Second import.
    |
    o  changeset:   0:60304fa41a49
       user:        Markus Zapke-Gründemann <markus@keimlink.de>
       date:        Tue Jul 10 10:19:10 2012 +0200
       summary:     importfs commit.

How to set up a development environment
=======================================

If you havn't created a clone of the importfs repository yet it's time
to do it now::

    $ hg clone https://bitbucket.org/keimlink/hg-importfs

Setup a virtualenv
------------------

The best way to do the development is to use a virtualenv_. So first
create one using virtualenvwrapper_::

    $ mkvirtualenv --distribute hg-importfs

Then install all packages needed for development into the virtualenv
using pip_::

    (hg-importfs)$ cd hg-importfs
    (hg-importfs)$ pip install -r requirements.txt

You also need a clone of the hg repository::

    (hg-importfs)$ cd ..
    (hg-importfs)$ hg clone http://selenic.com/repo/hg

Update to your desired version (if you don't want to use *tip*) and
build for local use::

    (hg-importfs)$ cd hg
    (hg-importfs)$ hg up VERSION
    (hg-importfs)$ make local

After creating the clone create a few symlinks in your importfs repository::

    (hg-importfs)$ cd ../hg-importfs
    (hg-importfs)$ ln -s ../hg/contrib/pylintrc
    (hg-importfs)$ ln -s ../hg/tests/hghave
    (hg-importfs)$ ln -s ../hg/tests/run-tests.py

Finally add the hg directory to your virtualenv::

    (hg-importfs)$ add2virtualenv ../hg

Run the tests
-------------

To run all tests you can now execute the following command::

    (hg-importfs)$ ./run-tests.py -l

Create a new source distribution package
----------------------------------------

A new Python source distribution package can be created using this command::

    (hg-importfs)$ python setup.py sdist

.. _Mercurial: http://mercurial.selenic.com/
.. _Lantiq: http://www.lantiq.com/
.. _Markus Zapke-Gründemann: http://www.keimlink.de/
.. _downloading: http://mercurial.selenic.com/downloads/
.. _pip: http://www.pip-installer.org/
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _virtualenvwrapper: http://pypi.python.org/pypi/virtualenvwrapper
