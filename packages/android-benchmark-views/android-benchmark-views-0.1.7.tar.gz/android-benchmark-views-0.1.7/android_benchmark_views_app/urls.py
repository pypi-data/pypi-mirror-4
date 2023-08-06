# Copyright (C) 2012 Linaro Limited
#
# Author: Andy Doan <andy.doan@linaro.org>
#
# This file is part of LAVA Android Benchmark Views.
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

from django.conf.urls.defaults import url, patterns

urlpatterns = patterns(
    'android_benchmark_views_app.views',
    url(r'^reports$', 'index'),
    url(r'^reports/(?P<series>[a-zA-Z0-9-\.]+)/$', 'report'),
    url(r'^reports/(?P<series>[a-zA-Z0-9-\.]+)/(?P<run>\d+)/$', 'run_summary'),
    )
