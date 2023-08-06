##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################

import z3c.form.interfaces
import z3c.formui.interfaces


class IPreferenceLayer(z3c.form.interfaces.IFormLayer):
    """Layer for z3c.preference."""


class IPreferenceSkin(z3c.formui.interfaces.IDivFormLayer,
                      IPreferenceLayer):
    """Skin for z3c.preference."""
