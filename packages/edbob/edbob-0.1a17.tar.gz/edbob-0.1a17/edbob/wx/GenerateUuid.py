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

import wx

# begin wxGlade: extracode
# end wxGlade

import edbob


class GenerateUuidDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: GenerateUuidDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, "&UUID:")
        self.Uuid = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        self.Generate = wx.Button(self, -1, "&Generate UUID")
        self.Close = wx.Button(self, wx.ID_OK, "&Close")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnGenerateButton, self.Generate)
        # end wxGlade

        self.GenerateUuid()

    def __set_properties(self):
        # begin wxGlade: GenerateUuidDialog.__set_properties
        self.SetTitle("Generate UUID")
        self.Uuid.SetMinSize((300, -1))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: GenerateUuidDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.label_1, 0, 0, 0)
        sizer_2.Add(self.Uuid, 0, wx.TOP|wx.EXPAND, 5)
        sizer_3.Add(self.Generate, 0, 0, 0)
        sizer_3.Add(self.Close, 0, wx.LEFT, 10)
        sizer_2.Add(sizer_3, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 10)
        sizer_1.Add(sizer_2, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.Centre()
        # end wxGlade

    def OnGenerateButton(self, event): # wxGlade: GenerateUuidDialog.<event_handler>
        self.GenerateUuid()
        event.Skip()

    def GenerateUuid(self):
        self.Uuid.SetValue(edbob.get_uuid())
        self.Uuid.SetSelection(-1, -1)
        self.Uuid.SetFocus()

# end of class GenerateUuidDialog


def main():
    app = wx.PySimpleApp()
    dlg = GenerateUuidDialog(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()


if __name__ == "__main__":
    main()
