#!/usr/bin/env python
from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()


version = '0.9dev'

install_requires = [
    'lxml',
    'pyyaml',
    'eventlet',
    'pyXMLSecurity',
    'cherrypy',
    'iso8601',
    'simplejson',
    'mako',
    'httplib2'
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='pyFF',
    version=version,
    description="Federation Feeder",
    long_description=README + '\n\n' + NEWS,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='identity federation saml metadata',
    author='Leif Johansson',
    author_email='leifj@sunet.se',
    url='http://blogs.mnt.se',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    package_data = {
        'pyff': ['xslt/*.xsl',
		'site/static/js/*',
		'site/static/css/*',
		'site/templates/*',
		'site/icons/*',
		'site/static/bootstrap/js/*',
		'site/static/bootstrap/css/*',
		'site/static/bootstrap/img/*',
		'schema/*.xsd']
    },
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['pyff=pyff:main','pyffd=pyff.mdx:main']
    },
    requires=install_requires
)
