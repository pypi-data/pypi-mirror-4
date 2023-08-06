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

import datetime

from django import forms
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    )
from django.template import RequestContext
from django.shortcuts import (
    get_object_or_404,
    render_to_response,
    )

from lava_server.views import index as lava_index
from lava_server.bread_crumbs import (
    BreadCrumb,
    BreadCrumbTrail,
)

from lava_kernel_ci_views_app.helpers import (
    DayCollection,
    DAY_DELTA,
    WEEK_DELTA,
    )
from lava_kernel_ci_views_app.models import BoardType


@BreadCrumb("Kernel CI", parent=lava_index)
def index(request):
    return render_to_response(
        "lava_kernel_ci_views_app/index.html",
        {
            'board_types': BoardType.objects.all().order_by('slug'),
            'bread_crumb_trail': BreadCrumbTrail.leading_to(index),
        }, RequestContext(request))


class DateRange(forms.Form):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)


@BreadCrumb("Tests run on {board_desc}", parent=index)
def per_board(request, board_type):

    board_type = get_object_or_404(BoardType, slug=board_type)

    form = DateRange(request.GET)
    form.is_valid()
    start = form.cleaned_data['start']
    if start is None:
        start = datetime.date.today() - WEEK_DELTA + DAY_DELTA

    end = form.cleaned_data['end']
    if end is None:
        end = datetime.date.today() + DAY_DELTA

    day_collection = DayCollection(board_type.slug, start, end)

    day_collection.evaluate(fetch_builds=True)

    link_prefix = reverse(
        'dashboard_app.views.redirect_to_bundle',
        kwargs={'content_sha1':'aaaaaaaaaaaaaaaaaaaaaaaaaaaa'}
        ).replace('aaaaaaaaaaaaaaaaaaaaaaaaaaaa/', '')

    test_run_prefix = reverse(
        'dashboard_app.views.redirect_to_test_run',
        kwargs={'analyzer_assigned_uuid':'aaaaaaaaaaaaaaaaaaaaaaaaaaaa'}
        ).replace('aaaaaaaaaaaaaaaaaaaaaaaaaaaa/', '')

    data = day_collection.json_ready()
    newer_results_link = None
    self_link = reverse(per_board, kwargs=dict(board_type=board_type.slug))
    if end <= datetime.date.today() + DAY_DELTA:
        newer_start = end
        newer_end = max(
            newer_start + WEEK_DELTA, datetime.date.today())
        newer_results_link = (
            self_link + '?start=' + newer_start.strftime('%Y-%m-%d') +
            '&end=' + newer_end.strftime('%Y-%m-%d'))
    older_end = start
    older_start = older_end - WEEK_DELTA
    older_results_link = (
        self_link + '?start=' + older_start.strftime('%Y-%m-%d') +
        '&end=' + older_end.strftime('%Y-%m-%d'))
    return render_to_response(
        "lava_kernel_ci_views_app/per_board.html",
        {
            'data': data,
            'link_prefix': link_prefix,
            'test_run_prefix': test_run_prefix,
            'newer_results_link': newer_results_link,
            'older_results_link': older_results_link,
            'bread_crumb_trail': BreadCrumbTrail.leading_to(
                per_board, board_desc=board_type.display_name),
            'include_tests': True,
            'board_type': board_type,
        }, RequestContext(request))


@BreadCrumb("Compile-only Results", parent=index)
def compile_view(request):

    form = DateRange(request.GET)
    form.is_valid()
    start = form.cleaned_data['start']
    if start is None:
        start = datetime.date.today() - WEEK_DELTA + DAY_DELTA

    end = form.cleaned_data['end']
    if end is None:
        end = datetime.date.today() + DAY_DELTA

    day_collection = DayCollection(None, start, end)

    day_collection.evaluate(fetch_builds=False)

    link_prefix = reverse(
        'dashboard_app.views.redirect_to_bundle',
        kwargs={'content_sha1':'aaaaaaaaaaaaaaaaaaaaaaaaaaaa'}
        ).replace('aaaaaaaaaaaaaaaaaaaaaaaaaaaa/', '')

    data = day_collection.json_ready()
    newer_results_link = None
    self_link = reverse(compile_view)
    if end <= datetime.date.today() + DAY_DELTA:
        newer_start = end
        newer_end = max(
            newer_start + WEEK_DELTA, datetime.date.today())
        newer_results_link = (
            self_link + '?start=' + newer_start.strftime('%Y-%m-%d') +
            '&end=' + newer_end.strftime('%Y-%m-%d'))
    older_end = start
    older_start = older_end - WEEK_DELTA
    older_results_link = (
        self_link + '?start=' + older_start.strftime('%Y-%m-%d') +
        '&end=' + older_end.strftime('%Y-%m-%d'))
    return render_to_response(
        "lava_kernel_ci_views_app/compile_only.html",
        {
            'data': data,
            'link_prefix': link_prefix,
            'newer_results_link': newer_results_link,
            'older_results_link': older_results_link,
            'bread_crumb_trail': BreadCrumbTrail.leading_to(compile_view),
            'include_tests': False,
        }, RequestContext(request))

def board_icon(request, board_type):
    board_type = get_object_or_404(BoardType, slug=board_type)
    response = HttpResponse(board_type.icon, content_type='image/png')
    return response
