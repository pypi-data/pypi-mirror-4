import multiprocessing
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from setuptools.command.test import test as TestCommand

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

py_version = sys.version_info[:2]

PY3 = py_version[0] == 3

if PY3:
    if py_version < (3, 2):
        raise RuntimeError('On Python 3, Space requires Python 3.2 or better')
else:
    if py_version < (2, 6):
        raise RuntimeError('On Python 2, Space requires Python 2.6 or better')

version = "0.0.3"

packages = [
    'space',
    'space.modules',
]

requires = [
    'argparse',
    'prettytable'
]

tests_require = [
    'docutils==0.10',
    'mock >= 1.0.1',
    'coverage==3.6',
    'mock==1.0.1',
    'py==1.4.12',
    'pytest==2.3.4',
    'pytest-cov==1.6',
    'coveralls==0.1.1'
]

if not PY3:
    tests_require.append('unittest2')


from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            'tests/unit',
            '--capture=sys',
            '--cov=space',
            '--cov-report=html'
        ]
        self.test_suite = True

    def run_tests(self):
         #import here, cause outside the eggs aren&#039;t loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='python-space',
    version=version,
    description='A command line tool for the Spacewalk API',
    long_description=open('README.rst').read() + '\n\n' +
                     open('CHANGES.rst').read(),
    author='David Johansen',
    author_email='david@makewhatis.com',
    url='https://space.readthedocs.org',
    packages=packages,
    package_dir={'space': 'space'},
    install_requires=requires,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'space = space.main:main',
        ],
    },
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
