##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Sample generator to create a intids utility inside a site.
"""
import zope.event
import zope.lifecycleevent
from zope.interface import implementer
from zope.intid import IntIds
from zope.intid.interfaces import IIntIds

from z3c.sampledata.interfaces import ISampleDataPlugin

@implementer(ISampleDataPlugin)
class SampleIntIds(object):

    dependencies = []
    schema = None

    def generate(self, context, param={}, dataSource={}, seed=None):
        """Generate an IntId utility inside context.

        'context' must be a site manager.
        """
        if 'omit' in param or context is None:
            return None
        sm = context.getSiteManager()
        default = sm['default']

        if 'intid' not in default:
            intid = IntIds()
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(intid))
            default['intid'] = intid
            sm.registerUtility(intid, IIntIds)
            return intid
        else:
            return default['intid']
