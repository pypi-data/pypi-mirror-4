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
    "tgext.pluggable",
    "tgext.datahelpers >= 0.0.5"
]

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(
    name='tgapp-userprofile',
    version='0.0.3',
    description='''Pluggable application for TurboGears2 which provides a basic user profile page with
forms to allow users to edit their own profile or change their password''',
    long_description=README,
    author='Mirko Darino, Alessandro Molina',
    author_email='mirko.darino@axant.it, alessandro.molina@axant.it',
    url='https://bitbucket.org/_amol_/tgapp-userprofile',
    keywords='turbogears2.application',
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=[],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    package_data={'tgapp.userprofile': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    entry_points="""
    """,
    dependency_links=[
        "http://www.turbogears.org/2.1/downloads/current/"
        ],
    zip_safe=False
)
