import os
from distutils.core import setup

version = "0.5"

doc_dir = os.path.join(os.path.dirname(__file__), "docs")
index_filename = os.path.join(doc_dir, "index.txt")
long_description = """\
Having to manually manage temporary directories is annoying.
So this class encapsulates temporary directories which just disappear after use,
including contained directories and files.
Temporary directories are created with tempfile.mkdtemp and thus save from race conditions.
Cleanup might not work on windows if files are still opened.
"""

setup(name='tempdir',
        version=version,
        description="Tempdirs are temporary directories, based on tempfile.mkdtemp",
        long_description=long_description,
        py_modules=['tempdir'],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Testing"
            ],
        keywords="temporary directory",
        author="Thomas Fenzl",
        author_email="thomas.fenzl+tempdir@gmail.com",
        url="https://bitbucket.org/another_thomas/tempdir",
        license="MIT",
        )


