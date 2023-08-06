from distutils.core import setup

long_description = open('README.rst').read()

from clime import __version__

setup(
    name    = 'clime',
    description = 'A Python module let you quickly convert the functions into a multi-command CLI program',
    long_description = long_description,
    version = __version__,
    author  = 'Mosky',
    author_email = 'mosky.tw@gmail.com',
    url = 'http://clime.mosky.tw/',
    packages = ['clime'],
)
