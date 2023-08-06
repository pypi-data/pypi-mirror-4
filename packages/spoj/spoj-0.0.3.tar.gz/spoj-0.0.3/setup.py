import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "spoj",
    version = "0.0.3",
    author = "Nyambayar Turbat",
    author_email = "t.nyambayar@gmail.com",
    description = ("command line tool for spoj.com "),
    license = "BSD",
    keywords = "spoj spoj.com algorithm",
    url = "http://packages.python.org/spoj",
    package_dir={'': 'spoj'},
    packages=find_packages('spoj'),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Topic :: Education",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Customer Service",
    ],
    install_requires=[
        'argparse>=1.2.1',
        'requests>=1.1.0',
        'BeautifulSoup>=3.2.1',
        ],
    entry_points={
        'console_scripts': [
            'spoj = spoj.main',
            ]
        },
)
