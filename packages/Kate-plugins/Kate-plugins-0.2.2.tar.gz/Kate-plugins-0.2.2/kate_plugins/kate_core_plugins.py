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

from PyKDE4.kdecore import KConfig, KConfigGroup
from PyKDE4.ktexteditor import KTextEditor

from PyQt4 import QtGui

TEXT_TO_CHANGE = 'XXX'
PREFIX_MENU = 'kate_plugins'


def insertText(text, strip_line=False,
               start_in_current_column=False,
               delete_spaces_initial=False,
               move_to=True):
    currentDocument = kate.activeDocument()
    view = currentDocument.activeView()
    currentPosition = view.cursorPosition()
    spaces = ''
    if strip_line:
        text = '\n'.join([line.strip() for line in text.splitlines()])
    if start_in_current_column:
        number_of_spaces = currentPosition.position()[1]
        spaces = ' ' * number_of_spaces
        text = '\n'.join([i > 0 and '%s%s' % (spaces, line) or line
                            for i, line in enumerate(text.splitlines())])
    if delete_spaces_initial:
        currentPosition.setColumn(0)
    currentDocument.insertText(currentPosition, text)
    text_to_change_len = len(TEXT_TO_CHANGE)
    if move_to and TEXT_TO_CHANGE in text:
        currentPosition = view.cursorPosition()
        pos_xxx = text.index(TEXT_TO_CHANGE)
        lines = text[pos_xxx + text_to_change_len:].count('\n')
        column = len(text[:pos_xxx].split('\n')[-1]) - currentPosition.column()
        setSelectionFromCurrentPosition((-lines, column), (-lines, column + text_to_change_len))


def is_mymetype_python(doc, text_plain=False):
    mimetype = unicode(doc.mimeType())
    if mimetype == 'text/x-python':
        return True
    elif mimetype == 'text/plain' and text_plain:
        return True
    return False


def is_mymetype_js(doc, text_plain=False):
    mimetype = unicode(doc.mimeType())
    if mimetype == 'application/javascript':
        return True
    elif mimetype == 'text/plain' and text_plain:
        return True
    return False


def get_session():
    main_window = kate.mainWindow()
    title = unicode(main_window.windowTitle())
    session = None
    if title and title != 'Kate' and ":" in title:
        session = title.split(":")[0]
        if session == 'file':
            session = None
    if session:
        return session
    return get_last_session()


def get_last_session():
    config = KConfig('katerc')
    kgroup = KConfigGroup(config, "General")
    session = kgroup.readEntry("Last Session")
    if session:
        session = unicode(session)
        session = session.replace('.katesession', '')
        return session
    return None


def setSelectionFromCurrentPosition(start, end, pos=None):
    view = kate.activeView()
    pos = pos or view.cursorPosition()
    cursor1 = KTextEditor.Cursor(pos.line() + start[0], pos.column() + start[1])
    cursor2 = KTextEditor.Cursor(pos.line() + end[0], pos.column() + end[1])
    view.setSelection(KTextEditor.Range(cursor1, cursor2))
    view.setCursorPosition(cursor1)


def findMenu(menu_parent_slug):
    window = kate.mainWindow()
    for menu in window.findChildren(QtGui.QMenu):
        if str(menu.objectName()) == menu_parent_slug:
            return menu
    return None


def get_slug_menu(slug_menu, prefix=PREFIX_MENU):
    if prefix and not slug_menu.startswith(PREFIX_MENU):
        slug_menu = '%s_%s' % (prefix, slug_menu)
    return slug_menu


def move_menu_submenu(menu_slug, submenu_slug):
    menu = findMenu(menu_slug)
    submenu = findMenu(submenu_slug)
    action_menubar = action_of_menu(submenu)
    action = QtGui.QAction(action_menubar.text(), submenu)
    action.setObjectName(action_menubar.text())
    action.setMenu(submenu)
    if action_menubar:
        action_menubar.deleteLater()
    menu.addAction(action)


def action_of_menu(menu):
    actions = [action for action in menu.parent().actions() if action.menu() and action.menu().objectName() == menu.objectName()]
    if len(actions) == 1:
        return actions[0]
    return None


def separated_menu(menu_parent_slug):
    menu_parent = findMenu(menu_parent_slug)
    action = QtGui.QAction('', None)
    menu_parent.insertSeparator(action)


def ipdb(with_position=True):
    import os
    import sys
    home = os.getenv("HOME")
    version = sys.version_info
    prefix = sys.prefix
    version = '%s%s' % (version[0], version[1])
    sys.path.insert(-1, os.path.join(prefix, 'lib/pymodules/python%s/IPython/Extensions' % version))
    sys.path.insert(-1, os.path.join(home, '.ipython'))
    sys.argv = [os.path.join(prefix, 'bin/ipython')]
    if with_position:
        currentDocument = kate.activeDocument()
        view = currentDocument.activeView()
        currentPosition = view.cursorPosition()
    import ipdb
    ipdb.set_trace()


def pdb():
    import pdb
    pdb.set_trace()
