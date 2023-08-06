#!/usr/bin/env python
#
# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
#
# This file is part of lava-scheduler-tool.
#
# lava-scheduler-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-scheduler-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-scheduler-tool.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name = 'lava-scheduler-tool',
    version = '0.6',
    author = "Linaro Validation Team",
    author_email = "linaro-dev@lists.linaro.org",
    packages = find_packages(),
    description = "Command line utility for the LAVA scheduler (deprecated)",
    url='https://launchpad.net/lava-scheduler-tool',
#    test_suite='lava_scheduler_tool.tests.test_suite',
    license="LGPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing",
    ],
    install_requires=['lava-tool >= 0.7.dev'],
    setup_requires = ['versiontools >= 1.3.1'],
    zip_safe = True,
)
