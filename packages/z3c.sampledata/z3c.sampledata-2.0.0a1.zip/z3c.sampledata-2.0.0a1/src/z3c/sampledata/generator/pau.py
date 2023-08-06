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
"""Sample generator to create a pau inside a site.
"""
import zope.event
import zope.lifecycleevent
from zope.interface import implementer

from zope.pluggableauth import PluggableAuthentication
from zope.authentication.interfaces import IAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder

from z3c.sampledata.interfaces import ISampleDataPlugin


@implementer(ISampleDataPlugin)
class SamplePau(object):

    dependencies = []
    schema = None

    def generate(self, context, param={}, dataSource={}, seed=None):
        """Generate a pay utility inside context.

        'context' must be a site manager.
        """
        if 'omit' in param or context is None:
            return None
        sm = context.getSiteManager()
        default = sm['default']

        if 'pau' not in default:
            pau = PluggableAuthentication()
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(pau))
            default['pau'] = pau
            sm.registerUtility(pau, IAuthentication)
            # create a principal folder
            pfNames = (u'members',)
            pau.authenticatorPlugins = pfNames
            for name in pfNames:
                if name in pau:
                    continue
                pf = PrincipalFolder(name +'.')
                zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(pf))
                default['pau'][name] = pf
                sm.registerUtility(pf, IAuthenticatorPlugin, name)
            return pau
        else:
            return default['pau']
