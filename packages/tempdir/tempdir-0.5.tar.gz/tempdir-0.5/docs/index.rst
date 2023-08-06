tempdir
=======

tempdir expands on mkdtemp from Python's stdlib tempfile module.
To download `visit the repository <https://bitbucket.org/another_thomas/tempdir>`_.



.. toctree::
    :maxdepth: 1

    news
    use
    license

Introduction
------------
The Python standard library allows to create temporary directories.
While useful, I find the requirement to handle the directory yourself is annoying.

That's why this module contains a little wrapper handling the temporary directory.

All files and directories contained in the temporary directory are deleted automatically.

