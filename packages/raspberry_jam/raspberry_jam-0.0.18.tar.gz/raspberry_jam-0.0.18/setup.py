import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "raspberry_jam",
    version = "0.0.18",
    author = "Ralph Saunders",
    author_email = "ralph@ralphsaunders.co.uk",
    description = ("Raspberry Jam for music"),
    license = "Private",
    keywords = "music",
    url = "http://example.com",
    packages=['app', 'app.raspberry_jam', 'app.spider'],

    package_data = {
        '' : ['app/raspberry_jam/static/*', 'app/raspberry_jam/templates/*']
    },
    long_description=read('README'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: Other/Proprietary License",
    ]
)
