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
    description=DESCRIPTION,
    long_description=open('README.md').read(),
)

