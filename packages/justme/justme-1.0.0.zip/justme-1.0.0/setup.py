#!/usr/bin/env python3

from distutils.core import setup

setup(
    name='justme',
    packages=['justme'],
    version='1.0.0',
    description='Prohibit to run two process/instance at same time.',
    author='梅どぶろく(umedoblock)',
    author_email='umedoblock@gmail.com',
    url='http://pypi.python.org/pypi/justme/',
    download_url='',
    license='BSD License',
    platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
    # see
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    options = {
        'sdist': {                                                                          'formats': ['gztar','zip'],
            'force_manifest': True,                                                     },
    },

    long_description = '''\
| Just me
| -------
| 
| Prohibit to run two process/instance at same time.
| to use a transaction behavior via sqlite3.
''',
     )
