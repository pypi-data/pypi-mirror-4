# -*- coding: utf-8 -*-
import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires=[
    "TurboGears2 >= 2.1.4",
    "tgext.pluggable >= 0.1.0",
    "tgext.tagging >= 0.2.1",
    "tgext.datahelpers",
    "tgext.ajaxforms",
    "tgext.crud >= 0.4"
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='tgapp-smallpress',
    version='0.5.4',
    description='Pluggable Minimalistic Blog for TurboGears2 with Attachments and Tags',
    long_description=README,
    author='Alessandro Molina',
    author_email='alessandro.molina@axant.it',
    url='http://bitbucket.org/_amol_/tgapp-smallpress',
    keywords='turbogears2.application',
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=[],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    package_data={'tgapp.smallpress': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    entry_points="""
    """,
    dependency_links=[
        "http://www.turbogears.org/2.1/downloads/current/"
        ],
    zip_safe=False
)
