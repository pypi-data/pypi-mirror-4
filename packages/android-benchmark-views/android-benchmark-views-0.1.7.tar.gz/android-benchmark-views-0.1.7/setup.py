#!/usr/bin/env python
#
# Copyright (C) 2012 Linaro Limited
#
# Author: Andy Doan <andy.doan@linaro.org>
#
# This file is part of LAVA Android Benchmark Views. Its based on the
# LAVA Kernel CI Views project.
#
# LAVA Android Benchmark Views is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License version 3 as
# published by the Free Software Foundation
#
# LAVA Android Benchmark Views is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Android Benchmark Views.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name='android-benchmark-views',
    version=":versiontools:android_benchmark_views_app:",
    author="Andy Doan",
    author_email="andy.doan@linaro.org",
    packages=find_packages(),
    license="AGPL",
    description="LAVA Android Benchmark Views Application",
    entry_points = """
        [lava_server.extensions]
        android-benchmark-views = android_benchmark_views_app.extension:AndroidBenchmarkViewsExtension
        """,
    long_description="""
    XXX
    """,
    install_requires=[
        "lava-server",
        'south >= 0.7.3',
        'versiontools >= 1.8',
    ],
    setup_requires=[
        'versiontools >= 1.8',
    ],
    zip_safe=False,
    include_package_data=True)
