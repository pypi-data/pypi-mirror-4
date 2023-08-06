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

from django.db import models

# Create your models here.

class BoardType(models.Model):

    slug = models.SlugField()

    display_name = models.TextField()

    icon = models.FileField(upload_to="board_icons")

    def __unicode__(self):
        return "%s board type" % self.slug
