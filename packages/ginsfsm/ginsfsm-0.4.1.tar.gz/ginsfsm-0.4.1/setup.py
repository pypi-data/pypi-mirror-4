# -*- encoding: utf-8 -*-

import os
import sys
import ginsfsm

from setuptools import setup, find_packages

if sys.version_info[:2] < (2, 6):
    raise RuntimeError('Requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

setup(name='ginsfsm',
    version=ginsfsm.__version__,
    description='GinsFSM, a library to develop systems based in '
                'finite-state machines',
    long_description=README + "\n\n",  # + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Communications",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
    ],

    keywords='framework communication fsm finite state machine fsm wsgi http '
             'socket poll epoll kqueue select server client workflow',
    author='Ginés Martínez',
    author_email='ginsmar at artgins.com',
    url='http://ginsfsm.org',
    license='MIT License',
    packages=find_packages(exclude=[]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'PasteDeploy >= 1.5.0',  # py3 compat
    ],
    extras_require=dict(
        rst=[
            'docutils',
            'svgwrite',
            'pillow',
        ],
    ),
    tests_require=[],
    test_suite="ginsfsm.tests",
    entry_points="""
        [ginsfsm.scaffold]
        simple_gobj=ginsfsm.scaffolds:SimpleGObjTemplate
        simple_wsgi=ginsfsm.scaffolds:SimpleWsgiTemplate
        multiple_wsgi=ginsfsm.scaffolds:MultipleWsgiTemplate

        [console_scripts]
        gcreate = ginsfsm.scripts.gcreate:main
        gserve = ginsfsm.scripts.gserve:main
    """,
    )
