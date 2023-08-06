# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
#
# This file is part of LAVA Kernel CI Views.
#
# LAVA Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Server.  If not, see <http://www.gnu.org/licenses/>.

import versiontools
from lava_server.extension import LavaServerExtension

import lava_kernel_ci_views_app


class KernelCIViewsExtension(LavaServerExtension):
    """
    Kernel CI Views Tracker extension.
    """

    @property
    def app_name(self):
        return "lava_kernel_ci_views_app"

    @property
    def name(self):
        return "Kernel CI"

    @property
    def main_view_name(self):
        return "lava_kernel_ci_views_app.views.index"

    @property
    def description(self):
        return "Kernel CI Views application for LAVA server"

    @property
    def version(self):
        return versiontools.format_version(lava_kernel_ci_views_app.__version__)

    def contribute_to_settings(self, settings_module):
        super(KernelCIViewsExtension, self).contribute_to_settings(settings_module)
        prepend_label_apps = settings_module.get('STATICFILES_PREPEND_LABEL_APPS', [])
        if self.app_name in prepend_label_apps:
            prepend_label_apps.remove(self.app_name)
