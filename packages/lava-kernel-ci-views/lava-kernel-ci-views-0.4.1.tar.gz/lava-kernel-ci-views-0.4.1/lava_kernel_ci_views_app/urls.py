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

from django.conf.urls.defaults import url, patterns

urlpatterns = patterns(
    'lava_kernel_ci_views_app.views',
    url(r'index$', 'index'),
    url(r'compile$', 'compile_view'),
    url(r'per_board/(?P<board_type>[a-zA-Z0-9_]+)$', 'per_board'),
    url(r'board_icon/(?P<board_type>[a-zA-Z0-9_]+)$', 'board_icon'),
    )
