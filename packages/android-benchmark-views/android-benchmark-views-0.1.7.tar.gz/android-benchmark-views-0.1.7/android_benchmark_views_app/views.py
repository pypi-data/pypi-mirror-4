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

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

import dashboard_app.views

from android_benchmark_views_app.models import (
    BenchmarkReport,
    BenchmarkRun,
)

from lava_server.bread_crumbs import (
    BreadCrumb,
    BreadCrumbTrail,
)


@BreadCrumb(
    "Android Benchmarks",
    parent=None
)
def index(request):
    reports = BenchmarkReport.objects.filter(can_publish=True).order_by('series').reverse()
    history_reports = reports
    if reports.count() > 6:
        history_reports = reports[6:]

    # fake out data so that we can compare GCC 4.6 performance
    # over the last 6 months
    report = BenchmarkReport()
    report_index = BenchmarkReport.objects.filter(series='index')
    if report_index.count() == 1:
        report = report_index[0]

    runs = []
    for r in history_reports:
        run = BenchmarkRun()
        run.report = report
        run.label = r.series
        b = BenchmarkRun.objects.filter(report=r, label='linaro-4.6')
        run.bundle = b[0].bundle
        runs.append(run)

    return render_to_response(
        "android_benchmark_views_app/index.html", {
            'report': report,
            'reports': reports,
            'runs': runs,

            'bread_crumb_trail': BreadCrumbTrail.leading_to(index)
        }, RequestContext(request))

@BreadCrumb(
    "{series}",
    parent=index,
    needs = ['series']
)
def report(request, series):
    br   = get_object_or_404(BenchmarkReport, series=series)
    runs = BenchmarkRun.objects.filter(report=br)

    return render_to_response(
        "android_benchmark_views_app/report.html", {
            'report': br,
            'runs': runs,

            'bread_crumb_trail': BreadCrumbTrail.leading_to(
                    report, series=series)
        }, RequestContext(request))

@BreadCrumb(
    "{run} Results",
    parent=report,
    needs=['series', 'run'])
def run_summary(request, series, run):
    report = get_object_or_404(BenchmarkReport, series=series)
    run = get_object_or_404(BenchmarkRun, pk=run)

    test_averages = run.get_test_averages()

    bundle_url = run.bundle.get_permalink()

    return render_to_response(
        "android_benchmark_views_app/run.html", {
            'report': report,
            'run': run,
            'test_averages': test_averages,
            'bundle_url': bundle_url,

            'bread_crumb_trail': BreadCrumbTrail.leading_to(
                    run_summary, series=series, run=run.label)
        }, RequestContext(request))
