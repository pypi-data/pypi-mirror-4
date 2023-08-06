import os

from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-serene",
    version = "0.0.9",
    author = "The Sirisanthana Team",
    author_email = "vsirisanthana@gmail.com",
    url = "http://code.google.com/p/django-serene/",
    description = "An enhanced djangorestframework. Serene is a RESTful framework with a touch of sirisanthana",
    long_description = read('README.txt'),
    download_url = "http://pypi.python.org/pypi/django-serene",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)"
    ],
    license = "GPL-3.0",
    keywords = "RESTful django djangorestframework",
    packages = ['serene', 'serene.tests'],
    install_requires = ['djangorestframework==0.3.3'],
)
