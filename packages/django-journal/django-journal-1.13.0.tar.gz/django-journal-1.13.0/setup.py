#!/usr/bin/python
import os

from setuptools import setup, find_packages
from setuptools.command.install_lib import install_lib as _install_lib
from distutils.command.build import build as _build
from distutils.command.sdist import sdist  as _sdist
from distutils.cmd import Command

class compile_translations(Command):
    description = 'compile message catalogs to MO files via django compilemessages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os
        import sys
        from django.core.management.commands.compilemessages import \
            compile_messages
        curdir = os.getcwd()
        os.chdir(os.path.realpath('django_journal'))
        compile_messages(stderr=sys.stderr)
        os.chdir(curdir)

class build(_build):
    sub_commands = [('compile_translations', None)] + _build.sub_commands

class sdist(_sdist):
    sub_commands = [('compile_translations', None)] + _sdist.sub_commands

class install_lib(_install_lib):
    def run(self):
        self.run_command('compile_translations')
        _install_lib.run(self)

setup(name='django-journal',
        version='1.13.0',
        license='AGPLv3',
        description='Keep a structured -- i.e. not just log strings -- journal'
                    ' of events in your applications',
        url='http://dev.entrouvert.org/projects/django-journal/',
        download_url='http://repos.entrouvert.org/django-journal.git/',
        author="Entr'ouvert",
        author_email="info@entrouvert.com",
        packages=find_packages(os.path.dirname(__file__) or '.'),
        include_package_data=True,
        package_data={'django_journal':
            ['locale/*/LC_MESSAGES/*.po',
             'locale/*/LC_MESSAGES/*.mo',
             'static/journal/css/*.css',
             'static/journal/images/*.png']},
        cmdclass={'build': build, 'install_lib': install_lib,
            'compile_translations': compile_translations,
            'sdist': sdist},
        install_requires=[
            'django >= 1.4.2, < 1.5',
        ],
)
