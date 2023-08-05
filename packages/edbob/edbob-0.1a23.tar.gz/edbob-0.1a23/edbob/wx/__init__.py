#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  edbob -- Pythonic Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of edbob.
#
#  edbob is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  edbob is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with edbob.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``edbob.wx`` -- wxPython Framework
"""

from __future__ import absolute_import

import wx


class ProgressDialog(wx.ProgressDialog):
    
    def __init__(self, parent, message, maximum, title="Processing...", can_abort=True, *args, **kwargs):
        style = wx.PD_SMOOTH|wx.PD_AUTO_HIDE|wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME|wx.PD_REMAINING_TIME
        if can_abort:
            style |= wx.PD_CAN_ABORT
        if 'style' in kwargs:
            style &= kwargs['style']
        kwargs['style'] = style
        wx.ProgressDialog.__init__(self, title, message, maximum=maximum, parent=parent, *args, **kwargs)
        
    def update(self, value, *args, **kwargs):
        if not wx.ProgressDialog.Update(self, value, *args, **kwargs)[0]:
            if self.ConfirmAbort():
                return False
            self.Resume()
        return True
        
    def destroy(self):
        self.Destroy()
        
    def ConfirmAbort(self):
        dlg = wx.MessageDialog(self, "Do you really wish to cancel this process?",
                               "Really Cancel?", wx.ICON_QUESTION|wx.YES_NO|wx.NO_DEFAULT)
        res = dlg.ShowModal()
        dlg.Destroy()
        return res == wx.ID_YES

        
class ProgressFactory(object):

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.args = args
        self.kwargs = kwargs

    def __call__(self, message, maximum, *args, **kwargs):
        message = '%s ...' % message
        args = self.args + args
        _kwargs = self.kwargs.copy()
        _kwargs.update(kwargs)
        return ProgressDialog(self.parent, message, maximum, *args, **_kwargs)


def LaunchDialog(dialog_class):
    """
    Creates a ``wx.PySimpleApp``, then instantiates ``dialog_class`` and shows
    it modally.
    """
    app = wx.PySimpleApp()
    dlg = dialog_class(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
