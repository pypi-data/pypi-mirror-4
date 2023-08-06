#!/usr/bin/env python
#
# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-dashboard-tool.
#
# lava-dashboard-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-dashboard-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-dashboard-tool.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name='lava-dashboard-tool',
    version="0.8",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    packages=find_packages(),
    description="Command line utility for Launch Control (deprecated)",
    url='https://launchpad.net/lava-dashboard-tool',
    test_suite='lava_dashboard_tool.tests.test_suite',
    license="LGPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing"],
    install_requires=[
        'lava-tool >= 0.7.dev',
    ],
    setup_requires=['versiontools >= 1.3.1'],
    tests_require=[],
    zip_safe=True)
