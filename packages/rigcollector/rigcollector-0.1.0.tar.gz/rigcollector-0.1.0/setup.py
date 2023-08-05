import os
import sys
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "rigcollector",
    version = "0.1.0",
    author = "Thomas Sileo",
    author_email = "thomas.sileo@gmail.com",
    description = "Collector for rigsmonitoring.com",
    license = "MIT",
    keywords = "monitoring metrics system",
    url = "https://github.com/RigsMonitoring/rigcollector",
    packages= ['rigcollector', 'rigcollector.custom'],
    long_description= read('README.rst'),
    install_requires=[
        "aaargh", "psutil", "pyyaml"
        ],
    entry_points={'console_scripts': ["rigcollector = rigcollector.app:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)