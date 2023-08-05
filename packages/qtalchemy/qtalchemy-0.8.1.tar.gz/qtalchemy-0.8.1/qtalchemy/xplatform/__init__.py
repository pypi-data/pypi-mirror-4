# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
This module contains tools to enable cross platform support.
"""

from stderr import StdErrEater, guiexcepthook

from util import is_windows, xdg_open
