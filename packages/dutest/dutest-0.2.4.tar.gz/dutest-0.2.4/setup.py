#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from dutest import __doc__ as DESC

versions = [
    (0, 1, 0),
    (0, 1, 1),
    (0, 1, 2),
    (0, 2, 1),
    (0, 2, 2),
    (0, 2, 3),
    (0, 2, 4),
    ]
    
latest = '.'.join(str(x) for x in versions[-1])
previous = '.'.join(str(x) for x in versions[-2])

status = {
            'beta' :      "Development Status :: 1 - Planning",
            'pre-alpha' : "Development Status :: 2 - Pre-Alpha",
            'alpha' :     "Development Status :: 3 - Alpha",
            'beta' :      "Development Status :: 4 - Beta",
            'stable' :    "Development Status :: 5 - Production/Stable",
            'mature' :    "Development Status :: 6 - Mature",
            'inactive' :  "Development Status :: 7 - Inactive"
         }
dev_status = status["alpha"]

cats = [
    dev_status,
    "Intended Audience :: Developers",
    "Intended Audience :: Information Technology",
    "License :: OSI Approved :: Python Software Foundation License",
    "Natural Language :: English",
    "Natural Language :: Spanish",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Documentation",
    "Topic :: Education :: Testing",
    "Topic :: Software Development :: Documentation",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Quality Assurance",
    "Topic :: Software Development :: Testing"
    ]

# Be compatible with older versions of Python
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# Add the change log to the package description.
chglog = None
try:
    from os.path import dirname, join
    chglog = open(join(dirname(__file__), "CHANGES.txt"))
    DESC+= ('\n\n' + chglog.read())
finally:
    if chglog:
        chglog.close()

setup(
	name='dutest',
	version=latest,
	description=DESC.split('\n', 1)[0],
	author='FLiOOPS Project',
	author_email='flioops@gmail.com',
	maintainer='Olemis Lang',
	maintainer_email='olemis@gmail.com',
	url='http://flioops.sourceforge.net',
	download_url='https://sourceforge.net/project/showfiles.php?group_id=220287&package_id=265911',
	package_dir = {'': 'utils'},
	requires = ['doctest', 'unittest'],
	provides = ['dutest (%s)' % (latest,)],
	obsoletes = ['dutest (<=%s)' % (previous,)],
	py_modules = ['dutest'],
	classifiers = cats,
	long_description= DESC
	)

