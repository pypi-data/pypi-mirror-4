##############################################################################
#
# Copyright (c) 2010, 2012 Zope Foundation and Contributors.
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

import z3c.form.field
import z3c.form.group
import z3c.formui.form
import zope.security.proxy


def to_fields(context):
    """Convert a preference group to a z3c.form.field.Field."""
    schema = zope.security.proxy.getObject(context.__schema__)
    if schema is None:
        # no schema set on preference group, so we have no fields
        return z3c.form.field.Fields()
    return z3c.form.field.Fields(schema)


class EditForm(z3c.formui.form.EditForm):
    """Edit form for preference groups."""

    def __init__(self, *args, **kw):
        super(EditForm, self).__init__(*args, **kw)
        self.label = self.context.__title__
        self.description = self.context.__description__
        self.fields = to_fields(self.context)


class PreferenceGroup(z3c.form.group.Group):
    """z3c.form group of a preference group."""

    def __init__(self, *args, **kw):
        super(PreferenceGroup, self).__init__(*args, **kw)
        self.fields = to_fields(self.context)
        self.description = self.context.__description__
        self.label = self.context.__title__


class CategoryEditForm(z3c.form.group.GroupForm,
                       EditForm):
    """Edit form for preference categories."""

    def __init__(self, *args, **kw):
        super(CategoryEditForm, self).__init__(*args, **kw)
        sorted_prefs = sorted(self.context.items(), key=lambda x: x[0])
        groups = [PreferenceGroup(pref, self.request, self)
                  for key, pref in sorted_prefs]
        self.groups = tuple(groups)
