import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cronsingleton",
    version = "1.0",
    author = "Adam Terrey",
    author_email = "arterrey@pretaweb.com",
    description = ("A user level cron cheduler."),
    license = "BSD",
    keywords = "cron",
    url = "http://packages.python.org/cronsingleton",
    packages=['cronsingleton'],
    long_description=read('README.rst'),
    classifiers=[
    ],
    install_requires=["apscheduler"],
    entry_points={
        'console_scripts': ['cronsingleton = cronsingleton.script:main']
        }
)

