# -*- coding: utf-8 -*-
# $Id: utils.py 228249 2010-12-05 01:02:42Z glenfant $
"""Misc utilities"""

from Products.Five import BrowserView
from config import CONTROLPANEL_ID
from controlpanel import ControlPanel

class Utils(BrowserView):

    def add(self):
        """Add the control panel
        """
        zcp = self.context.Control_Panel
        if CONTROLPANEL_ID not in zcp.objectIds():
            mpcp = ControlPanel()
            zcp._setObject(CONTROLPANEL_ID, mpcp)
        return u"Monkey pacher panel added. Click the \"Back\" button of your browser."

    def remove(self):
        """Removes the control panel
        """
        zcp = self.context.Control_Panel
        if CONTROLPANEL_ID not in zcp.objectIds():
            zcp._delObject(CONTROLPANEL_ID)
        return u"Monkey pacher panel removed. Click the \"Back\" button of your browser."
