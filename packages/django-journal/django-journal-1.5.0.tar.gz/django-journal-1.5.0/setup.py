#!/usr/bin/python
from setuptools import setup, find_packages
import os

setup(name='django-journal',
        version='1.5.0',
        license='AGPLv3',
        description='Keep a structured -- i.e. not just log strings -- journal'
                    ' of events in your applications',
        url='http://dev.entrouvert.org/projects/django-journal/',
        download_url='http://repos.entrouvert.org/django-journal.git/',
        author="Entr'ouvert",
        author_email="info@entrouvert.com",
        packages=find_packages(os.path.dirname(__file__) or '.'),
        install_requires=[
            'django >= 1.4.2, < 1.5',
        ],
)
