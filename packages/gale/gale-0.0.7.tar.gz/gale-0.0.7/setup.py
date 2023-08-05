import os
from distutils.core import setup

PACKAGE = "gale"
NAME = "gale"
DESCRIPTION = "Sugar for Tornado Asynchrous HTTP client"
AUTHOR = "simpx"
AUTHOR_EMAIL = "simpxx@gmail.com"
URL = 'https://github.com/simpx/gale'

setup(
    name=NAME,
    version=__import__(PACKAGE).__version__,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=['gale'],
    url=URL,
    license="BSD",
    long_description=open(os.path.join(os.path.dirname(__file__),"README.md"), "r").read(),
    install_requires=['tornado'],
    requires=['tornado'],
    description=DESCRIPTION
)

