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
"""Sample generator to create principals
"""
import zope.interface
import zope.component
import zope.event
import zope.schema
import zope.lifecycleevent
from zope.interface import implements
from zope.app.authentication import principalfolder
from zope.site import hooks

from z3c.sampledata.interfaces import ISampleDataPlugin

from z3c.sampledata import _


class IPrincipalDataSource(zope.interface.Interface):
    """A marker interface for principal data source adapters"""

def defaultPrincipalDataFactory(object):
     return [['batlogg', 'Jodok Batlogg', 'bJB'],
             ['jukart', 'Juergen Kartnaller', 'jJK'],
             ['dobee', 'Bernd Dorn', 'dBD'],
             ['srichter', 'Stephan Richter', 'sSR'],
             ['byzo', 'Michael Breidenbruecker', 'bMB'],
             ['oli', 'Oliver Ruhm', 'oOR']]


class ISamplePrincipalParameters(zope.interface.Interface):
    """The parameters for the sample principal generator."""

    minPrincipals = zope.schema.Int(
            title = _(u'Min principals'),
            description = _(u'Create at least this number of pricipals from'
                            u' the principals file.\n'
                            u'This has higher priority than maxPricipals.\n'
                            u'-1 : create all principals from the datasource.'
                           ),
            required = False,
            default = -1,
            )

    maxPrincipals = zope.schema.Int(
            title = _(u'Max principals'),
            description = _(u'The maximum number of principals to create.\n'
                            u'Uses the first principals from the datasource.'
                           ),
            required = False,
            default = -1,
            )

    pauLocation = zope.schema.TextLine(
            title = _(u'PAU location'),
            description = _(u'Path to the PAU inside the site manager.'),
            required = False,
            default = u'default/pau',
            )

    passwordManager = zope.schema.TextLine(
            title = _(u'Password Manager'),
            description = _(u'The password manager to use.'),
            required = False,
            default = u'SHA1',
            )


class SamplePrincipals(object):
    """Create principals inside a site manager.

    context : site
    return  : pau in which the principals where created
    """

    implements(ISampleDataPlugin)

    dependencies = []
    schema = ISamplePrincipalParameters

    maxPrincipals = None
    minPrincipals = None

    def generate(self, context, param={}, dataSource=[], seed=None):
        """Generate sample pricipals"""
        if 'omit' in param or context is None:
            return None
        self.minPrincipals = int(param['minPrincipals'])
        if self.minPrincipals<0:
            self.minPrincipals = None
        self.maxPrincipals = int(param['maxPrincipals'])
        if self.maxPrincipals<0:
            self.maxPrincipals = None
        originalSite = hooks.getSite()
        hooks.setSite(context)
        sm = zope.component.getSiteManager(context)
        self.pau = self._getPAU(sm, param)
        self.passwordManagerName = param['passwordManager']

        numCreated = 0
        self.logins = []
        if dataSource:
            for info in dataSource:
                if (    self.maxPrincipals is not None
                    and numCreated>=self.maxPrincipals):
                    break
                login = unicode(info[0])
                if login in self.logins:
                    # ignore duplicate principals
                    continue
                self._createPrincipal(context, info)
                numCreated+=1

        if (    self.minPrincipals is not None
            and numCreated<self.minPrincipals):
            for i in range(self.minPrincipals-numCreated):
                info = self._createDummyPrincipalInfo(context, i)
                self._createPrincipal(context, info)

        hooks.setSite(originalSite)

        return self.pau

    def _getPAU(self, sm, param):
        pau = sm
        for loc in param['pauLocation'].split('/'):
            pau = pau[loc]
        return pau


    def _createPrincipal(self, site, info):
        login = unicode(info[0])
        self.logins.append(login)
        if login in self.pau['members']:
            return
        name = unicode(info[1])
        password = unicode(info[2])
        principal = principalfolder.InternalPrincipal(
                            login,
                            password,
                            name,
                            passwordManagerName=self.passwordManagerName)
        zope.event.notify(
            zope.lifecycleevent.ObjectCreatedEvent(principal))
        self.pau['members'][login] = principal

    def _createDummyPrincipalInfo(self, site, i):
        return ['login%i'%i, 'name%i'%i, '%i'%i]
