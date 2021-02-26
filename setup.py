#!/usr/bin/env python3

import datetime
import os.path
from setuptools import find_packages, setup

setup(
    name="scigateway-auth",
    version="0+" + datetime.date.today().isoformat(),
    url="https://github.com/ral-facilities/scigateway-auth",
    packages=find_packages(include=["scigateway_auth", "scigateway_auth.*"]),
    package_data={"scigateway_auth": ["config.json.example"]},
    classifiers=[
        "Framework :: Flask",
        "Programming Language :: Python :: 3",
    ],
    install_requires=open(
        os.path.join(os.path.dirname(__file__), "requirements.txt"), "r"
    )
    .read()
    .splitlines(),
)
