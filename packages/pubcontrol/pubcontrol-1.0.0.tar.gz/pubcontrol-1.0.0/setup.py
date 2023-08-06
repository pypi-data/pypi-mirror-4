#!/usr/bin/env python

from distutils.core import setup

setup(
name="pubcontrol",
version="1.0.0",
description="EPCP library",
author="Justin Karneges",
author_email="justin@affinix.com",
url="https://github.com/fanout/pypubcontrol",
py_modules=["pubcontrol"],
requires=["PyJWT (>=0.1.5)", "pyzmq (>=2.0, <3.0)"],
license="MIT",
classifiers=[
	"Topic :: Utilities",
	"License :: OSI Approved :: MIT License"
]
)
