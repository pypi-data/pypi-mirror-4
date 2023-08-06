Use
---

TempDir implements the contextmanager protocol. 
So it can be used in a with-statements as follows:

>>> with tempdir.TempDir() as t:
...     <create files and directories>
...
>>> #all gone

It can also be used in a regular way:

>>> t = tempdir.TempDir()
>>> # do things
>>> t.dissolve()

The parameters are like tempfile.mkdtemp.

If you have a code block where you need to change the current working directory, there is a convenience-wrapper in_tempdir:

>>> with in_tempdir():
>>> #  os.chdir'ed into the temporary directory
>>>    pass
>>> # back in wherever you were before

and a function decorator:

>>> @run_in_tempdir():
>>> def function_in_tempdir(test):
>>> #   new working directory is created for every call
>>>     pass

Those ideas are based on work by Krisztian Fekete.
