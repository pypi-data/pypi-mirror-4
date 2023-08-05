#!/usr/bin/env python
"""Setup for autoflake."""

import sys


def version():
    """Return version string."""
    with open('autoflake.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                import ast
                return ast.literal_eval(line.split('=')[1].strip())


def pyflakes_installed():
    """Return True if pyflakes executable is installed."""
    import os
    import subprocess
    try:
        process = subprocess.Popen(
            ['pyflakes', os.devnull],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process.communicate()
        return True
    except OSError:
        return False


with open('README.rst') as readme:
    setup_arguments = {
        'name': 'autoflake',
        'version': version(),
        'description': 'Removes unused imports.',
        'long_description': readme.read(),
        'license': 'Expat License',
        'author': 'myint',
        'url': 'https://github.com/myint/autoflake',
        'classifiers': ['Intended Audience :: Developers',
                        'Environment :: Console',
                        'Programming Language :: Python :: 2.7',
                        'Programming Language :: Python :: 3',
                        'License :: OSI Approved :: MIT License'],
        'keywords': 'clean,automatic,unused,import',
        'py_modules': ['autoflake'],
        'scripts': ['autoflake'],
    }


# Don't bother trying to install pyflakes3k on 3.3. It is not compatible.
if pyflakes_installed() or sys.version_info >= (3, 3):
    from distutils import core
    core.setup(**setup_arguments)
else:
    # Only resort to setuptools if necessary.
    setup_arguments['install_requires'] = [
        'pyflakes' if sys.version_info[0] < 3 else 'pyflakes3k']

    import setuptools
    setuptools.setup(**setup_arguments)
