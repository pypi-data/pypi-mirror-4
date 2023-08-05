""" Installer
"""
import os
from setuptools import setup, find_packages

NAME = 'eea.forms'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
        version=VERSION,
        description="EEA forms - Custom AT widgets and fields",
        long_description=open("README.txt").read() + "\n" +
                         open(os.path.join("docs", "HISTORY.txt")).read(),
        classifiers=[
            "Framework :: Zope2",
            "Framework :: Zope3",
            "Framework :: Plone",
            "Framework :: Plone :: 4.0",
            "Framework :: Plone :: 4.1",
            "Framework :: Plone :: 4.2",
            "Programming Language :: Zope",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "License :: OSI Approved :: Mozilla Public License 1.0 (MPL)",
          ],
        keywords='eea forms plone widgets fields quickupload',
        author='European Environment Agency',
        author_email='webadmin@eea.europa.eu',
        maintainer='Alin Voinea (Eau de Web)',
        maintainer_email='alin@eaudeweb.ro',
        bugtrack_url="https://github.com/eea/eea.forms/issues",
        download_url="http://pypi.python.org/pypi/eea.forms",
        url='https://eea.github.com/docs/eea.forms',
        license='GPL',
        packages=find_packages(exclude=['ez_setup']),
        namespace_packages=['eea'],
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'setuptools',
            'collective.quickupload',
        ],
        extras_require={
            'test': ['plone.app.testing']
        },
        entry_points="""
        # -*- Entry points: -*-
        """,
    )
