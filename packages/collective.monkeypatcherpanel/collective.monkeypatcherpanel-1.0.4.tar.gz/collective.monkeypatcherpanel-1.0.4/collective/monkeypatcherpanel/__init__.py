# -*- coding: utf-8 -*-
# $Id: __init__.py 228249 2010-12-05 01:02:42Z glenfant $
"""collective.monkeypatcherpanel"""

import zope.component
from collective.monkeypatcher.interfaces import IMonkeyPatchEvent
from controlpanel import monkeyPatchAdded

# We need to register the event handler as soon as possible.
# Doing this as usual in ZCML will be too late.

gsm = zope.component.getGlobalSiteManager()
gsm.registerHandler(monkeyPatchAdded, (IMonkeyPatchEvent,))

def initialize(context):
    """Zope 2 registration"""
    # Maybe a future usage
    return
