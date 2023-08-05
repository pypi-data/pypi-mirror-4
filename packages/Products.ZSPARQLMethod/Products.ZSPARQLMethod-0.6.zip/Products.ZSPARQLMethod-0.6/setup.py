from setuptools import setup, find_packages
from os.path import join
import sys
import os

NAME = 'Products.ZSPARQLMethod'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(join(*PATH)).read().strip()

install_requires = ['sparql-client']
if sys.version_info < (2, 6):
    install_requires += ['simplejson']

docs = open('README.rst').read() + "\n" + \
       open(os.path.join("docs", "HISTORY.txt")).read()

setup(
    name=NAME,
    version=VERSION,
    keywords='sparql rdf linkeddata semanticweb zope python',
    author='European Environment Agency',
    author_email="webadmin@eea.europa.eu",
    url='https://svn.eionet.europa.eu/repositories/Zope/trunk/Products.ZSPARQLMethod',
    license="Mozilla Public License 1.1",
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Zope2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    description="Zope product for making SPARQL queries, simiar to ZSQLMethod",
    long_description=docs,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
