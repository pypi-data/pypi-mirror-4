# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='invenio-devserver',
    version='0.2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=False,
    zip_safe=False,
    install_requires=['distribute', 'werkzeug', 'mock'],
    entry_points={
        'console_scripts': [
            'serve = invenio_devserver.serve:main',
            'mailserve = invenio_devserver.mailserve:main',
        ],
    },

    # PyPI metadata
    author="Alessio Deiana",
    author_email="alessio.deiana@cern.ch",
    description=("An HTTP server for Invenio with automatic code reloading"),
    long_description=read('README'),
    license="GPL",
    keywords="invenio http server",
    url="https://bitbucket.org/osso/invenio-devserver",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
)
