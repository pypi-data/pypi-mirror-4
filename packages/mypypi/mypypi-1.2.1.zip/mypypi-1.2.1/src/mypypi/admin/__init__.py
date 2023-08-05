##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.i18n

from z3c.table import column

from mypypi.i18n import MessageFactory as _


# helper classes
class PublishedColumn(column.CheckBoxColumn):
    """PublishedColumn checkbox column."""

    header = _('Published')

    @apply
    def publishedItems():
        # use the items form the table
        def get(self):
            return self.table.publishedItems
        def set(self, values):
            self.table.publishedItems = values
        return property(get, set)

    def getItemKey(self, item):
        return '%s-publishedItems' % self.id

    def update(self):
        self.publishedItems = [item for item in self.table.values
                              if self.isSelected(item)]

    def renderCell(self, item):
        selected = u''
        state = _('No')
        if item.published:
            selected='checked="checked"'
            state = _('Yes')
        state = zope.i18n.translate(state, context=self.request)
        return u'<input type="checkbox" class="%s" name="%s" value="%s" %s /> (%s)' \
            %('checkbox-widget', self.getItemKey(item), self.getItemValue(item),
            selected, state)
