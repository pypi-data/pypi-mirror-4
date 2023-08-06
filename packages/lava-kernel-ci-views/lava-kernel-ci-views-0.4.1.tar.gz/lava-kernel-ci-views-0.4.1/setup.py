#!/usr/bin/env python
#
# Copyright (C) 2011 Linaro Limited
#
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
#
# This file is part of LAVA Kernel CI Views.
#
# LAVA Kernel CI Views is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License version 3 as
# published by the Free Software Foundation
#
# LAVA Kernel CI Views is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Kernel CI Views.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name='lava-kernel-ci-views',
    version=":versiontools:lava_kernel_ci_views_app:",
    author="Michael Hudson-Doyle",
    author_email="michael.hudson@linaro.org",
    packages=find_packages(),
    license="AGPL",
    description="LAVA Kernel CI Views Application",
    entry_points = """
        [lava_server.extensions]
        kernel-ci-views = lava_kernel_ci_views_app.extension:KernelCIViewsExtension
        """,
    long_description="""
    XXX
    """,
    install_requires=[
        "lava-server",
        'versiontools >= 1.8',
    ],
    setup_requires=[
        'versiontools >= 1.8',
    ],
    zip_safe=False,
    include_package_data=True)
