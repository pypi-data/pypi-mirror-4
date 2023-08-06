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

from django.db import models
from dashboard_app import models as lava_models

import android_benchmark_views_app.helpers as helpers

class BenchmarkReport(models.Model):
    """
    Model for representing a monthly Android Toolchain Benchmark.

    Monthly benchmarks compare results of android benchmarks that have been
    run with versions of android built for each toolchain to be tested.

    The series is normally something like "2012.02" for the 2012.02
    engineering cycle comparisons.
    """

    series = models.CharField(max_length=16, unique=True)

    comments = models.TextField(blank=True, null=False,
         help_text='Can be used to provide a bit of an executive summary to the report')

    can_publish = models.BooleanField(
            help_text='The report won\'t be listed in the main view for this project until this field gets enabled. This allows for an internal review of the results before "publishing" them.'
        )

    @models.permalink
    def get_absolute_url(self):
        return ('android_benchmark_views_app.views.report',
                [self.series])

    def __unicode__(self):
        return self.series

class BenchmarkRun(models.Model):
    """
    Models one benchmarking run ran with a build of a certain toolchain.

    The label is used to describe the toolchain used for the run,
    ie "linaro-4.6" or "android-4.4". The results of the run are a typical
    LAVA bundle
    """

    label  = models.CharField(max_length=16)
    report = models.ForeignKey(
                BenchmarkReport,
                related_name='benchmark_runs')
    bundle = models.ForeignKey(
                lava_models.Bundle,
                related_name='benchmark_runs')

    @models.permalink
    def get_absolute_url(self):
        return ('android_benchmark_views_app.views.run_summary',
                [self.report.series, self.pk])

    def __unicode__(self):
        return u'%s-%s' % (self.report.series, self.label)

    def get_test_averages(self):
        """see helpers.benchmark_run_test_averages for description """
        return helpers.benchmark_run_test_averages(self)

