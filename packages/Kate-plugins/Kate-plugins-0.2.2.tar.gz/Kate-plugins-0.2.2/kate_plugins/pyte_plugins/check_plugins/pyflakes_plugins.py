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

import _ast

import kate
from pyflakes.checker import Checker
from pyflakes.messages import Message

from kate_settings_plugins import KATE_ACTIONS
from pyte_plugins.check_plugins import commons
from pyte_plugins.check_plugins.check_all_plugins import checkAll


def pyflakes(codeString, filename):
    """
    Check the Python source given by C{codeString} for flakes.
    """
    # First, compile into an AST and handle syntax errors.
    try:
        tree = compile(codeString, filename, "exec", _ast.PyCF_ONLY_AST)
    except SyntaxError, value:
        msg = value.args[0]
        lineno = value.lineno
        # If there's an encoding problem with the file, the text is None.
        if value.text is None:
            # Avoid using msg, since for the only known case, it contains a
            # bogus message that claims the encoding the file declared was
            # unknown.
            msg = "Problem decoding source"
            lineno = 1
        error = Message(filename, lineno)
        error.message = msg + "%s"
        error.message_args = ""
        return [error]
    else:
        # Okay, it's syntactically valid.  Now check it.
        w = Checker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        return w.messages


@kate.action(**KATE_ACTIONS['checkPyflakes'])
def checkPyflakes(currentDocument=None, refresh=True):
    if not commons.canCheckDocument(currentDocument):
        return
    if refresh:
        checkAll.f(currentDocument, ['checkPyflakes'],
                 exclude_all=not currentDocument)
    move_cursor = not currentDocument
    currentDocument = currentDocument or kate.activeDocument()

    path = unicode(currentDocument.url().path())
    mark_key = '%s-pyflakes' % path

    text = unicode(currentDocument.text())
    errors = pyflakes(text.encode('utf-8', 'ignore'), path)
    errors_to_show = []

    if len(errors) == 0:
        commons.showOk("Pyflakes Ok")
        return

    # Prepare errors found for painting
    for error in errors:
        errors_to_show.append({
            "filename": path,
            "message": error.message % error.message_args,
            "line": error.lineno,
            })

    commons.showErrors('Pyflakes Errors:', errors_to_show,
                       mark_key, currentDocument,
                       move_cursor=move_cursor)
