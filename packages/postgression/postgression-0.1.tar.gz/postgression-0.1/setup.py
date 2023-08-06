from os.path import abspath, dirname, join, normpath

from setuptools import setup


setup(

    # Basic package information:
    name = 'postgression',
    version = '0.1',
    scripts = [
        'postgression',
    ],

    # Packaging options:
    zip_safe = False,
    include_package_data = True,

    # Package dependencies:
    install_requires = ['requests>=1.1.0'],

    # Metadata for PyPI:
    author = 'Randall Degges',
    author_email = 'rdegges@gmail.com',
    license = 'UNLICENSE',
    url = 'https://github.com/postgression/python-postgression',
    keywords = 'heroku cloud testing postgresql databases unit awesome epic',
    description = 'A python client for the postgression API.',
    long_description = open(normpath(join(dirname(abspath(__file__)),
        'README.md'))).read()

)
