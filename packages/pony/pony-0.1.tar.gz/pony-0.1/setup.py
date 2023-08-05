from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
from glob import glob
import sys

name = "pony"
version = "0.1"
description = "Pony Object Relational Mapper"
long_description = """Pony helps to simplify data management. Using Pony you can work with the data in terms of 
entities and their relationships. Pony also allows quering data in pure Python using the syntax of generator 
expressions."""

classifiers=[
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: Free for non-commercial use",
    "License :: OSI Approved :: GNU Affero General Public License v3",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries",
    "Topic :: Database"
]
author="Pony Team"
author_email="team@python-orm.com"
url="http://python-orm.com"
license="AGPL"

modules=[
    "pony.converting",
    "pony.dbapiprovider",
    "pony.dbschema",
    "pony.decompiling",
    "pony.options",
    "pony.orm",
    "pony.sqlbuilding",
    "pony.sqlsymbols",
    "pony.sqltranslation",
    "pony.utils"
]

packages=[
    "pony.examples",
    "pony.dbproviders"
]

download_url="http://pypi.python.org/pypi/pony/"

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


def main():
    python_version = sys.version_info
    if python_version < (2, 4) or python_version >= (2, 8):
        s = "Sorry, but %s %s requires Python version 2.4, 2.5, 2.6 or 2.7. You have version %s"
        print s % (name, version, python_version.split(' ', 1)[0])
        sys.exit(1)
    
    if sys.argv[1] == 'bdist_wininst':
        for fileInfo in data_files:
            fileInfo[0] = '\\PURELIB\\%s' % fileInfo[0]

    setup(
        name=name,
        version=version,
        description=description,
        long_description=long_description,
        classifiers=classifiers,
        author=author,
        author_email=author_email,
        url=url,
        license=license,
        packages=packages,
        download_url=download_url,
        py_modules=modules
    )

if __name__ == "__main__":
    main()
