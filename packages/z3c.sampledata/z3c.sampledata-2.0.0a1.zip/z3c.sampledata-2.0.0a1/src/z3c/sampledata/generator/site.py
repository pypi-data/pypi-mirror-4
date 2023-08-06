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
"""Sample generator to create a site.
"""
import zope.event
import zope.interface
import zope.lifecycleevent
import zope.schema
from zope.interface import implementer
from zope.site import hooks
from zope.site.folder import Folder
from zope.site.site import LocalSiteManager

from z3c.sampledata import _
from z3c.sampledata.interfaces import ISampleDataPlugin

class ISampleSiteParameters(zope.interface.Interface):
    """The parameters for the site creation."""

    sitename = zope.schema.TextLine(
            title = _(u'Sitename'),
            required = True,
            default = u'',
            )


@implementer(ISampleDataPlugin)
class SampleSite(object):

    dependencies = []
    schema = ISampleSiteParameters

    def generate(self, context, param={}, dataSource={}, seed=None):
        """Generate the site inside context"""
        if 'omit' in param:
            return None
        name = param['sitename']
        folder = Folder()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(folder))
        context[name] = folder
        sm = LocalSiteManager(folder)
        folder.setSiteManager(sm)
        hooks.setSite(folder)
        return folder
