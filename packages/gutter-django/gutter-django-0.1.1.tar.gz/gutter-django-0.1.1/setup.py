#!/usr/bin/env python

import sys
import os
from setuptools import find_packages


try:
    from notsetuptools import setup
except ImportError:
    from setuptools import setup

try:
    import multiprocessing
except ImportError:
    pass

tests_require = ['nose', 'unittest2', 'describe==1.0.0beta1', 'exam']

dependency_links = [
    'https://github.com/jeffh/describe/tarball/dev#egg=describe'
]

install_requires = [
    'nexus>=0.2.3', 'gutter>=0.1.1', 'django'
]

dependency_links = [
    'https://github.com/jeffh/describe/tarball/dev#egg=describe'
]

setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)


setup(
    name='gutter-django',
    version='0.1.1',
    author='DISQUS',
    author_email='opensource@disqus.com',
    url='http://github.com/disqus/gutter-django',
    description = 'Web UI to administer Gutter switches.',
    packages=find_packages(exclude=["example_project", "tests"]),
    zip_safe=False,
    install_requires=install_requires,
    setup_requires=setup_requires,
    license='Apache License 2.0',
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)