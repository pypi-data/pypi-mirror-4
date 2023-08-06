#!/usr/bin/env python
import setuptools

setuptools.setup(name='niice',
    version='0.0.1.0',
    author='mkorenkov',
    author_email = "mkorenkov@gmail.com",
    description = 'In-house metrics collection engine.',
    long_description='RevelSystems in-house metrics collection engine.', #open('README.md').read(),
    license = "Proprietary, All rights reserved.",
    url = "https://github.com/Revel-Systems/niice",
    scripts=['bin/niice', 'bin/niiced', 'bin/niice_hwinfo'],
    packages=setuptools.find_packages(exclude=['bin', 'niice_couch']),
    install_requires = [
        "pika",
        "CouchDB",
        "PyYAML",
        "pytz",
        "psutil"
    ]
)