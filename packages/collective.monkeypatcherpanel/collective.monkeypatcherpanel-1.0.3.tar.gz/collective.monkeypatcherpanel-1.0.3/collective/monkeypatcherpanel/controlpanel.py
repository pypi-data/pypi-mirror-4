# -*- coding: utf-8 -*-
# $Id: controlpanel.py 146677 2010-10-21 15:24:51Z glenfant $
"""ZMI control panel"""

import Acquisition
from OFS import SimpleItem
from App.version_txt import getZopeVersion
version = getZopeVersion()
if version > (2, 12):
    class Fake:
        pass
else:
    from App.ApplicationManager import Fake

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from config import CONTROLPANEL_ID

all_patches = []

def monkeyPatchAdded(event):
    """See collective.monkeypatcher.interfaces.IMonkeyPatchEvent"""
    all_patches.append(event.patch_info)
    return


class ControlPanel(Fake, SimpleItem.Item, Acquisition.Implicit):
    """The Monkey patches control panel"""

    id = CONTROLPANEL_ID
    name = title = "Monkey Patches"
    manage_main = PageTemplateFile('zmi/controlpanel.pt', globals())

    manage_options=((
        {'label': 'Monkey Patches', 'action': 'manage_main'},
        ))

    def getId(self):
        return self.id

    def allPatches(self):
        return all_patches

