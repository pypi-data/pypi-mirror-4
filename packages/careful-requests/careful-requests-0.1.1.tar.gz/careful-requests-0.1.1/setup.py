# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="careful-requests",
    version="0.1.1",
    url="https://github.com/kanzure/careful-requests",
    license="BSD",
    author="Bryan Bishop",
    author_email="kanzure@gmail.com",
    description="Requests for header-sensitive servers (like Accept-Encoding)",
    long_description=open("README.rst", "r").read(),
    packages=["careful_requests"],
    zip_safe=False,
    include_package_data=True,
    install_requires=["requests"],
    platforms="any",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        'Natural Language :: English',
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        #"Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ]
)
