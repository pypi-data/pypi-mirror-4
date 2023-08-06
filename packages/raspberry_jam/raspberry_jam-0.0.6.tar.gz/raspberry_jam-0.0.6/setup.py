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
    version = "0.0.6",
    author = "Ralph Saunders",
    author_email = "ralph@ralphsaunders.co.uk",
    description = ("Raspberry Jam for music"),
    license = "Private",
    keywords = "music",
    url = "http://example.com",
    packages=['app', 'app.raspberry_jam', 'app.spider'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: Other/Proprietary License",
    ],
    install_requires = [
        "Flask==0.9",
        "Jinja2==2.6",
        "Werkzeug==0.8.3",
        "certifi==0.0.8",
        "chardet==2.1.1",
        "fudge==1.0.3",
        "nose==1.1.2",
        "psycopg2==2.4.5",
        "readline==6.2.4.1",
        "requests==0.10.1",
        "simplejson==2.6.2",
        "soundcloud==0.3.1",
        "tornado==2.4",
        "wsgiref==0.1.2"
    ]
)
