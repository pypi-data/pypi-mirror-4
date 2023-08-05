# -*- coding: utf-8 -*-
# $Id: setup.py 251030 2012-09-20 10:01:21Z ajung $
from setuptools import setup, find_packages
import os

def read(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = read('collective', 'monkeypatcherpanel', 'version.txt')

setup(
    name='collective.monkeypatcherpanel',
    version=version,
    description="A Zope 2 control panel that shows monkey patches applied by collective.monkeypatcher",
    long_description=(read("README.txt")
                      + "\n\n"
                      + read('docs', 'HISTORY.txt')),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='zope monkey patch panel',
    author='Gilles Lenfant',
    author_email='gilles.lenfant@gmail.com',
    url='http://pypi.python.org/pypi/collective.monkeypatcherpanel',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'collective.monkeypatcher'
        ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target=plone
    """,
    )
