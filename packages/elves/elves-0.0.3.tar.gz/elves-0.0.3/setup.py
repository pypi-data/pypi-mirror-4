from distutils.core import setup

PACKAGE = "elves"
NAME = "elves"
DESCRIPTION = "Python Thread For Human"
AUTHOR = "simpx"
AUTHOR_EMAIL = "simpxx@gmail.com"
URL = 'https://github.com/simpx/elves'

setup(
    name=NAME,
    version=__import__(PACKAGE).__version__,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=['elves'],
    url=URL,
    license="BSD",
    description=DESCRIPTION,
    long_description=open('README').read()
)

