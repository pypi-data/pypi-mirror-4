# -*- coding: utf-8 -*-
# Copyright (c) 2011 by Pablo Martín <goinnn@gmail.com>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

import kate

from kate_core_plugins import insertText, TEXT_TO_CHANGE
from kate_settings_plugins import KATE_ACTIONS

TEXT_JQUERY = """<script type="text/javascript">
    (function($){
        $(document).ready(function () {
            $("%s").click(function(){
                // Write here
            });
        });
      })(jQuery);
</script>
"""


@kate.action(**KATE_ACTIONS['insertReady'])
def insertReady():
    insertText(TEXT_JQUERY % TEXT_TO_CHANGE, start_in_current_column=True)
