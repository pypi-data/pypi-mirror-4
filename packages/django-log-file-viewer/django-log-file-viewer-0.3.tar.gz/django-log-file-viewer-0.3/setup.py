#!/usr/bin/env python

from distutils.core import setup

setup(name='django-log-file-viewer',
    version='0.3',
    description='Django admin expansion to read/parse file based Django Logging output.',
    author='Iurii Garmash',
    author_email='garmon1@gmail.com',
    url='http://garmoncheg.blogspot.com/2012/09/django-log-files-viewer-documents.html',
    packages=['django-log-file-viewer'],
    package_dir={'django-log-file_viewer': 'src/django-log-file-viewer'},
    package_data={'django-log-file-viewer': [
        'templates/*.html',
        'testdata/log/test/.gitignore', # To keep this directory (required for farther tests)
        'testdata/log/testlog.log',
        'README.rst',
        'README',
        ]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: Log Analysis',
        'Topic :: System :: Logging',
        'Topic :: System :: Systems Administration',
        'Topic :: Text Processing',
        ],
)