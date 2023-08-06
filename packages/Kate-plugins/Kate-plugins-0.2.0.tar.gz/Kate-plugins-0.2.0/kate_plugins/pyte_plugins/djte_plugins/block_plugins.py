# -*- coding: utf-8 -*-
# Copyright (c) 2013 by Pablo Martín <goinnn@gmail.com>
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
import re
from kate_core_plugins import insertText
from kate_settings_plugins import KATE_ACTIONS, TEMPLATE_TAGS_CLOSE
from pyte_plugins.text_plugins import str_blank


@kate.action(**KATE_ACTIONS['closeTemplateTag'])
def closeTemplateTag():
    template_tags = '|'.join(TEMPLATE_TAGS_CLOSE)
    pattern_tag_open = re.compile("(.)*{%%%(espaces)s(%(tags)s)%(espaces)s(.)*%(espaces)s%%}(.)*" % {'espaces': str_blank, 'tags': template_tags})
    pattern_tag_close = re.compile("(.)*{%%%(espaces)send(%(tags)s)%(espaces)s%(espaces)s%%}(.)*" % {'espaces': str_blank, 'tags': template_tags})
    tag_closes = {}
    currentDocument = kate.activeDocument()
    view = currentDocument.activeView()
    currentPosition = view.cursorPosition()
    currentLine = currentPosition.line()
    tag = ''
    while currentLine >= 0:
        text = unicode(currentDocument.line(currentLine))
        match_open = pattern_tag_open.match(text)
        if match_open:
            tag_name = match_open.groups()[1]
            if tag_name in tag_closes:
                tag_closes[tag_name] -= 1
                if tag_closes[tag_name] == 0:
                    del tag_closes[tag_name]
            elif not tag_closes:
                tag = match_open.groups()[1]
                break
        else:
            match_close = pattern_tag_close.match(text)
            if match_close:
                tag_name = match_close.groups()[1]
                tag_closes[tag_name] = tag_closes.get(tag_name, 0) + 1
        currentLine = currentLine - 1
    insertText("{%% end%s %%}" % tag)


@kate.action(**KATE_ACTIONS['createBlock'])
def createBlock():
    currentDocument = kate.activeDocument()
    view = currentDocument.activeView()
    source = view.selectionText()
    try:
        block_type, block_source = source.split("#")
    except ValueError:
        block_type = 'block'
        block_source = source
    view.removeSelectionText()
    insertText("{%% %(block_type)s %(block_source)s %%}XXX{%% end%(block_type)s %%}" %
                {'block_type': block_type, 'block_source': block_source})
